# -*- encoding: utf-8 -*-
import logging

from datetime import date
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
    def requested(self):
        return self.model.objects.get(slug=self.model.REQUESTED)

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
        customer = Customer.objects.get(email=content_object.checkout_email)
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
    """Checkout."""

    action = models.ForeignKey(CheckoutAction)
    customer = models.ForeignKey(Customer)
    state = models.ForeignKey(CheckoutState, default=default_checkout_state)
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

    def current(self):
        """List of payment plan headers excluding 'deleted'."""
        return self.model.objects.exclude(deleted=True)


class PaymentPlan(TimeStampedModel):
    """Definition of a payment plan."""

    name = models.TextField()
    slug = models.SlugField(unique=True)
    deposit = models.IntegerField(help_text='Initial deposit as a percentage')
    count = models.IntegerField(help_text='Number of payments')
    interval = models.IntegerField(help_text='Payment interval in months')
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
            raise ValidationError('Set at least one installment.')
        if not self.deposit:
            raise ValidationError('Set an initial deposit.')
        if not self.interval:
            raise ValidationError('Set the number of months between installments.')

    def illustration(self, start_date, total):
        # list of deposit and installment dates
        dates = [d.date() for d in rrule(
            MONTHLY,
            dtstart=start_date,
            count=self.count+1
        )]
        # deposit
        deposit = (
            total * (self.deposit / Decimal('100'))
        ).quantize(Decimal('.01'))
        # installments
        installment = (
            (total - deposit) / self.count
        ).quantize(Decimal('.01'))
        # list of payment amounts
        values = []
        check = Decimal()
        for idx, d in enumerate(dates):
            if idx == 0:
                value = deposit
            else:
                value = installment
            values.append(value)
            check = check + value
        # make the total match
        values[-1] = values[-1] + (total - check)
        return list(zip(dates, values))

    @property
    def example(self):
        return self.illustration(date.today(), Decimal('100'))

reversion.register(PaymentPlan)


class ContactPlanManager(models.Manager):

    def create_contact_plan(self, contact, payment_plan, start_date, total):
        """Create a payment plan.

        This method must be called from within a transaction.

        """
        obj = self.model(contact=contact, payment_plan=payment_plan)
        obj.save()
        installments = payment_plan.illustration(start_date, total)
        for due, amount in installments:
            ContactPlanPayment.objects.create_contact_plan_payment(
                obj,
                due,
                amount
            )
        return obj


class ContactPlan(TimeStampedModel):
    """Payment plan for a contact."""

    contact = models.ForeignKey(settings.CONTACT_MODEL)
    payment_plan = models.ForeignKey(PaymentPlan)
    deleted = models.BooleanField(default=False)
    objects = ContactPlanManager()

    class Meta:
        ordering = ('contact__user__username', 'payment_plan__slug')
        verbose_name = 'Contact payment plan'
        verbose_name_plural = 'Contact payment plans'

    def __str__(self):
        return '{} {}'.format(self.contact.user.username, self.payment_plan.name)

    @property
    def payments(self):
        return self.contactplanpayment_set.all().order_by('due')

reversion.register(ContactPlan)


class ContactPlanPaymentManager(models.Manager):

    def create_contact_plan_payment(self, contact_plan, due, amount):
        obj = self.model(contact_plan=contact_plan, due=due, amount=amount)
        obj.save()
        return obj

    @property
    def _lock_due(self):
        """Lock the records while we try and take the payment."""
        return self.model.objects.select_for_update(
            nowait=True
        ).filter(
            due__gte=date.today(),
            state__slug=CheckoutState.PENDING,
        ).exclude(
            contact_plan__deleted=True,
        )

    @property
    def process_payments(self):
        with transaction.atomic():
            pks = [o.pk for o in self._lock_due]
            for pk in pks:
                print(pk)


class ContactPlanPayment(TimeStampedModel):
    """Payments for a contact."""

    contact_plan = models.ForeignKey(ContactPlan)
    state = models.ForeignKey(CheckoutState, default=default_checkout_state)
    due = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    objects = ContactPlanPaymentManager()

    class Meta:
        unique_together = ('contact_plan', 'due')
        verbose_name = 'Payments for a contact'
        verbose_name_plural = 'Payments for a contact'

    def __str__(self):
        return '{} {} {} {}'.format(
            self.contact_plan.contact.user.username,
            self.contact_plan.payment_plan.name,
            self.due,
            self.amount,
        )

reversion.register(ContactPlanPayment)
