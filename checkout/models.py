# -*- encoding: utf-8 -*-
import logging

from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import (
    MONTHLY,
    rrule,
)
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import (
    models,
    transaction,
)

import reversion
import stripe

from base.model_utils import TimeStampedModel
from mail.models import Notify
from mail.service import queue_mail_message


CURRENCY = 'GBP'
logger = logging.getLogger(__name__)


def as_pennies(total):
    return int(total * Decimal('100'))


def default_checkout_state():
    return CheckoutState.objects.get(slug=CheckoutState.PENDING).pk


def log_stripe_error(log, e, message):
    log.error(
        'StripeError\n'
        '{}\n'
        'http body: {}\n'
        'http status: {}'.format(
            message,
            e.http_body,
            e.http_status,
        )
    )


class CheckoutError(Exception):

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr('%s, %s' % (self.__class__.__name__, self.value))


class CheckoutStateManager(models.Manager):

    @property
    def fail(self):
        return self.model.objects.get(slug=self.model.FAIL)

    @property
    def pending(self):
        return self.model.objects.get(slug=self.model.PENDING)

    @property
    def request(self):
        return self.model.objects.get(slug=self.model.REQUEST)

    @property
    def success(self):
        return self.model.objects.get(slug=self.model.SUCCESS)


class CheckoutState(TimeStampedModel):

    FAIL = 'fail'
    PENDING = 'pending'
    REQUEST = 'request'
    SUCCESS = 'success'

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    objects = CheckoutStateManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Checkout state'
        verbose_name_plural = 'Checkout states'

    def __str__(self):
        return '{}'.format(self.name)

reversion.register(CheckoutState)


class CheckoutActionManager(models.Manager):

    @property
    def payment(self):
        return self.model.objects.get(slug=self.model.PAYMENT)

    @property
    def payment_plan(self):
        return self.model.objects.get(slug=self.model.PAYMENT_PLAN)


class CheckoutAction(TimeStampedModel):

    PAYMENT = 'payment'
    PAYMENT_PLAN = 'payment_plan'

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    objects = CheckoutActionManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Checkout action'
        verbose_name_plural = 'Checkout action'

    def __str__(self):
        return '{}'.format(self.name)

reversion.register(CheckoutAction)


class CustomerManager(models.Manager):

    def _create_customer(self, name, email, customer_id):
        obj = self.model(name=name, email=email, customer_id=customer_id)
        obj.save()
        return obj

    def _stripe_create(self, email, description, token):
        """Use the Stripe API to create a customer."""
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.create(
                email=email,
                description=description,
                card=token,
            )
            return customer.id
        except stripe.StripeError as e:
            log_stripe_error(logger, e, '_stripe_create - email: {}'.format(email))
            raise CheckoutError('Error creating Stripe customer') from e

    def _stripe_update(self, customer_id, description, token):
        """Use the Stripe API to update a customer."""
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_customer = stripe.Customer.retrieve(customer_id)
            stripe_customer.description = description
            stripe_customer.card = token
            stripe_customer.save()
        except stripe.StripeError as e:
            log_stripe_error(logger, e, '_stripe_update - id: {}'.format(customer_id))
            raise CheckoutError('Error updating Stripe customer') from e

    def init_customer(self, content_object, token):
        """Initialise Stripe customer using email, description and token.

        1. Lookup existing customer record in the database.

           - Retrieve customer from Stripe and update description and token.

        2. If the customer does not exist:

          - Create Stripe customer with email, description and token.
          - Create a customer record in the database.

        Return the customer database record.

        """
        name = content_object.checkout_name
        email = content_object.checkout_email
        try:
            obj = self.model.objects.get(email=email)
            obj.name = name
            obj.save()
            self._stripe_update(obj.customer_id, name, token)
        except self.model.DoesNotExist:
            customer_id = self._stripe_create(email, name, token)
            obj = self._create_customer(name, email, customer_id)
        return obj


class Customer(TimeStampedModel):
    """Stripe Customer.

    Link the Stripe customer to an email address (and name).

    Note: It is expected that multiple users in our databases could have the
    same email address.  If they have different names, then this table looks
    very confusing.  Try checking the 'content_object' of the 'Checkout' model
    if you need to diagnose an issue.

    """

    name = models.TextField()
    email = models.EmailField(unique=True)
    customer_id = models.TextField()
    expiry_date = models.DateField(blank=True, null=True)
    objects = CustomerManager()

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return '{} {}'.format(self.email, self.customer_id)

reversion.register(Customer)


class CheckoutManager(models.Manager):

    def _create_checkout(self, action, customer, description, content_object):
        """Create a checkout payment request."""
        obj = self.model(
            action=action,
            content_object=content_object,
            customer=customer,
            description=description,
        )
        obj.save()
        return obj

    def audit(self):
        return self.model.objects.all().order_by('-pk')

    def direct_debit(self, content_object):
        """Collect some money from a customer.

        We should only attempt to collect money if the customer has already
        entered their card details.

        """
        try:
            customer = Customer.objects.get(
                email=content_object.checkout_email
            )
        except Customer.DoesNotExist as e:
            raise CheckoutError(
                'Customer has not registered a card'
            ) from e
        checkout = self.pay(
            CheckoutAction.objects.payment,
            customer,
            content_object
        )
        with transaction.atomic():
            checkout.success()

    def pay(self, action, customer, content_object):
        obj = self._create_checkout(
            action,
            customer,
            ', '.join(content_object.checkout_description),
            content_object,
        )
        if obj.payment:
            obj.total = content_object.checkout_total
            obj.save()
            # Create the charge on stripe's servers
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.Charge.create(
                amount=as_pennies(content_object.checkout_total),
                currency=CURRENCY,
                customer=customer.customer_id,
                description=obj.description,
            )
        return obj

    def success(self):
        return self.audit().filter(state=CheckoutState.objects.success)


class Checkout(TimeStampedModel):
    """Checkout.

    Create a 'Checkout' instance when you want to interact with Stripe e.g.
    take a payment, get card details to set-up a payment plan or refresh the
    details of an expired card.

    """

    action = models.ForeignKey(
        CheckoutAction
    )
    customer = models.ForeignKey(Customer)
    state = models.ForeignKey(
        CheckoutState,
        default=default_checkout_state
        #blank=True,
        #null=True
    )
    description = models.TextField()
    total = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    # link to the object in the system which requested the checkout
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    objects = CheckoutManager()

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Checkout'
        verbose_name_plural = 'Checkouts'

    def __str__(self):
        return '{}'.format(self.customer.email)

    def _success_or_fail(self, state):
        self.state = state
        self.save()

    @property
    def content_object_url(self):
        try:
            return self.content_object.get_absolute_url()
        except AttributeError:
            return None

    @property
    def fail(self):
        """Checkout failed - so update and notify admin."""
        self._success_or_fail(CheckoutState.objects.fail)
        return self.object.checkout_fail()

    @property
    def failed(self):
        """Did the checkout request fail?"""
        return self.state == CheckoutState.objects.fail

    def notify(self, request):
        email_addresses = [n.email for n in Notify.objects.all()]
        if email_addresses:
            caption = self.action.name
            subject = '{} from {}'.format(
                caption.capitalize(),
                self.customer.name,
            )
            message = '{} - {} from {}, {}:'.format(
                self.created.strftime('%d/%m/%Y %H:%M'),
                caption,
                self.customer.name,
                self.customer.email,
            )
            message = message + '\n\n{}\n\n{}'.format(
                self.description,
                request.build_absolute_uri(self.content_object_url),
            )
            queue_mail_message(
                self,
                email_addresses,
                subject,
                message,
            )
        else:
            logging.error(
                "Cannot send email notification of checkout transaction.  "
                "No email addresses set-up in 'enquiry.models.Notify'"
            )

    @property
    def payment(self):
        """Is this a payment action."""
        return self.action == CheckoutAction.objects.payment

    def success(self):
        """Checkout successful - so update and notify admin."""
        self._success_or_fail(CheckoutState.objects.success)
        return self.content_object.checkout_success()

reversion.register(Checkout)


class PaymentPlanManager(models.Manager):

    def create_payment_plan(self, slug, name, deposit, count, interval):
        obj = self.model(
            slug=slug,
            name=name,
            deposit=deposit,
            count=count,
            interval=interval,
        )
        obj.save()
        return obj

    def current(self):
        """List of payment plan headers excluding 'deleted'."""
        return self.model.objects.exclude(deleted=True)


class PaymentPlan(TimeStampedModel):
    """Definition of a payment plan."""

    name = models.TextField()
    slug = models.SlugField(unique=True)
    deposit = models.IntegerField(help_text='Initial deposit as a percentage')
    count = models.IntegerField(help_text='Number of instalments')
    interval = models.IntegerField(help_text='Instalment interval in months')
    deleted = models.BooleanField(default=False)
    objects = PaymentPlanManager()

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Payment plan'
        verbose_name_plural = 'Payment plan'

    def __str__(self):
        return '{}'.format(self.slug)

    def clean(self):
        if not self.count:
            raise ValidationError('Set at least one instalment.')
        if not self.deposit:
            raise ValidationError('Set an initial deposit.')
        if not self.interval:
            raise ValidationError('Set the number of months between instalments.')

    def deposit_amount(self, total):
        return (
            total * (self.deposit / Decimal('100'))
        ).quantize(Decimal('.01'))

    def instalments(self, total):
        # deposit
        deposit = self.deposit_amount(total)
        # list of dates
        start_date = date.today() + relativedelta(months=+self.interval)
        instalment_dates = [d.date() for d in rrule(
            MONTHLY,
            count=self.count,
            dtstart=start_date,
            interval=self.interval,
        )]
        # instalments
        instalment = (
            (total - deposit) / self.count
        ).quantize(Decimal('.01'))
        # list of payment amounts
        values = []
        check = deposit
        for d in instalment_dates:
            value = instalment
            values.append(value)
            check = check + value
        # make the total match
        values[-1] = values[-1] + (total - check)
        return list(zip(instalment_dates, values))

    def example(self, total):
        result = [
            (date.today(), self.deposit_amount(total)),
        ]
        return result + self.instalments(total)

reversion.register(PaymentPlan)


class ContactPaymentPlanManager(models.Manager):

    def create_contact_payment_plan(
            self, contact, content_object, payment_plan, total):
        """Create a payment plan for the contact with the deposit record.

        This method must be called from within a transaction.

        """
        obj = self.model(
            contact=contact,
            content_object=content_object,
            payment_plan=payment_plan,
            total=total,
        )
        obj.save()
        ContactPaymentPlanInstalment.objects.create_contact_payment_plan_instalment(
            obj,
            ContactPaymentPlanInstalment.DEPOSIT,
            payment_plan.deposit_amount(total),
            None
        )
        return obj


class ContactPaymentPlan(TimeStampedModel):
    """Payment plan for a contact."""

    contact = models.ForeignKey(settings.CONTACT_MODEL)
    payment_plan = models.ForeignKey(PaymentPlan)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    # link to the object in the system which requested the payment plan
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    # is this object deleted?
    deleted = models.BooleanField(default=False)
    objects = ContactPaymentPlanManager()

    class Meta:
        ordering = ('contact__user__username', 'payment_plan__slug')
        unique_together = ('object_id', 'content_type')
        verbose_name = 'Contact payment plan'
        verbose_name_plural = 'Contact payment plans'

    def __str__(self):
        return '{} {}'.format(self.contact.user.username, self.payment_plan.name)

    @property
    def _check_create_instalments(self):
        """Check the current records to make sure we can create instalments."""
        instalments = ContactPaymentPlanInstalment.objects.filter(
            contact_payment_plan=self
        )
        count = instalments.count()
        if not count:
            # a contact payment plan should always have a deposit record
            raise CheckoutError(
                "no deposit/instalment record set-up for "
                "payment plan: '{}'".format(self.pk)
            )
        if count == 1:
            # the deposit record should have a 'count' of 1 (DEPOSIT)
            if not instalments.first().count == ContactPaymentPlanInstalment.DEPOSIT:
                raise CheckoutError(
                    "no deposit record for "
                    "payment plan: '{}'".format(self.pk)
                )
        else:
            # cannot create instalments if already created!
            raise CheckoutError(
                "instalments already created for this "
                "payment plan: '{}'".format(self.pk)
            )

    def create_instalments(self):
        self._check_create_instalments
        instalments = self.payment_plan.instalments(self.total)
        count = 1
        for due, amount in instalments:
            count = count + 1
            ContactPaymentPlanInstalment.objects.create_contact_payment_plan_instalment(
                self,
                count,
                amount,
                due,
            )

    @property
    def payment_count(self):
        return self.contactpaymentplaninstalment_set.count()

    @property
    def payments(self):
        return self.contactpaymentplaninstalment_set.all().order_by('due')

reversion.register(ContactPaymentPlan)


class ContactPaymentPlanInstalmentManager(models.Manager):

    def create_contact_payment_plan_instalment(
            self, contact_payment_plan, count, amount, due):
        obj = self.model(
            contact_payment_plan=contact_payment_plan,
            count=count,
            amount=amount,
            due=due,
        )
        obj.save()
        return obj

    @property
    def due(self):
        """Lock the records while we try and take the payment.

        TODO Do we need to check that a payment is not already linked to this
        record?

        """
        return self.model.objects.filter(
            due__gte=date.today(),
            state__slug=CheckoutState.PENDING,
        ).exclude(
            contact_payment_plan__deleted=True,
        )

    @property
    def process_payments(self):
        """Process pending payments.

        We set the status to 'request' before asking for the money.  This is
        because we can't put the payment request into a transaction.  If we are
        not careful, we could have a situation where the payment succeeds and
        we don't manage to set the state to 'success'.  In the code below, if
        the payment fails the record will be left in the 'request' state and
        so we won't not ask for the money again.

        """
        pks = [o.pk for o in self.due]
        for pk in pks:
            with transaction.atomic():
                # make sure the payment is still pending
                instalment = self.model.objects.select_for_update(
                    nowait=True
                ).get(
                    pk=pk,
                    state__slug=CheckoutState.PENDING
                )
                # we are ready to request payment
                instalment.state = CheckoutState.objects.request
                instalment.save()
            # request payment
            Checkout.objects.direct_debit(instalment)


class ContactPaymentPlanInstalment(TimeStampedModel):
    """Payments due for a contact.

    The deposit record gets created first.  It has:

    - ``count`` of ``1``
    - ``due`` date of ``null``

    The instalment records are created after the deposit has been collected.
    Instalment records have a ``due`` date and a ``count`` greater than ``1``.

    """

    # the 'count' should be set to 1 for the deposit
    DEPOSIT = 1

    contact_payment_plan = models.ForeignKey(ContactPaymentPlan)
    count = models.IntegerField()
    state = models.ForeignKey(
        CheckoutState,
        default=default_checkout_state,
        #blank=True,
        #null=True
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    due = models.DateField(blank=True, null=True)
    objects = ContactPaymentPlanInstalmentManager()

    class Meta:
        unique_together = (
            ('contact_payment_plan', 'due'),
            ('contact_payment_plan', 'count'),
        )
        verbose_name = 'Payments for a contact'
        verbose_name_plural = 'Payments for a contact'

    def __str__(self):
        return '{} {} {} {}'.format(
            self.contact_plan.contact.user.username,
            self.contact_plan.payment_plan.name,
            self.due,
            self.amount,
        )

    def get_absolute_url(self):
        """TODO Update this to display the payment plan."""
        return reverse('project.home')

    @property
    def checkout_description(self):
        return [
            '{}'.format(
                self.contact_payment_plan.payment_plan.name,
            ),
            'Instalment {} of {}'.format(
                self.count,
                self.contact_payment_plan.payment_count,
            ),
        ]

    @property
    def checkout_email(self):
        return self.contact_payment_plan.contact.user.email

    @property
    def checkout_fail(self):
        """Update the object to record the payment failure.

        Called from within a transaction and you can update the model.

        """
        self.state = CheckoutState.objects.fail
        self.save()

    @property
    def checkout_name(self):
        return self.contact_payment_plan.contact.user.get_full_name()

    @property
    def checkout_success(self):
        """Update the object to record the payment success.

        Called from within a transaction and you can update the model.

        """
        self.state = CheckoutState.objects.success
        self.save()

    @property
    def checkout_total(self):
        return self.amount

reversion.register(ContactPaymentPlanInstalment)
