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
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import (
    models,
    transaction,
)
from django.utils import timezone

import reversion
import stripe

from base.model_utils import TimeStampedModel
from base.singleton import SingletonModel
from mail.models import Notify
from mail.service import (
    queue_mail_message,
    queue_mail_template,
)


CURRENCY = 'GBP'
logger = logging.getLogger(__name__)


def _card_error(e):
    return (
        "CardError: param '{}' code '{}' http body '{}' "
        "http status '{}'".format(
            e.param,
            e.code,
            e.http_body,
            e.http_status,
        )
    )


def _stripe_error(e):
    return ("http body: '{}' http status: '{}'".format(
        e.http_body,
        e.http_status,
    ))


def as_pennies(total):
    return int(total * Decimal('100'))


def default_checkout_state():
    return CheckoutState.objects.get(slug=CheckoutState.PENDING).pk


def expiry_date_as_str(item):
    d = item.get('expiry_date', None)
    return d.strftime('%Y%m%d') if d else ''


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
        """The 'request' state is used for payment plans only.

        It allows the system to set the state to ``request`` before charging
        the account.

        """
        return self.model.objects.get(slug=self.model.REQUEST)

    @property
    def success(self):
        return self.model.objects.get(slug=self.model.SUCCESS)


class CheckoutState(TimeStampedModel):

    FAIL = 'fail'
    PENDING = 'pending'
    # The 'request' state is used for payment plans only.
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

    @property
    def is_success(self):
        return self.slug == self.SUCCESS

    @property
    def is_pending(self):
        return self.slug == self.PENDING

reversion.register(CheckoutState)


class CheckoutActionManager(models.Manager):

    @property
    def card_refresh(self):
        return self.model.objects.get(slug=self.model.CARD_REFRESH)

    @property
    def charge(self):
        return self.model.objects.get(slug=self.model.CHARGE)

    @property
    def invoice(self):
        return self.model.objects.get(slug=self.model.INVOICE)

    @property
    def manual(self):
        return self.model.objects.get(slug=self.model.MANUAL)

    @property
    def payment(self):
        return self.model.objects.get(slug=self.model.PAYMENT)

    @property
    def payment_plan(self):
        return self.model.objects.get(slug=self.model.PAYMENT_PLAN)


class CheckoutAction(TimeStampedModel):

    CARD_REFRESH = 'card_refresh'
    CHARGE = 'charge'
    INVOICE = 'invoice'
    MANUAL = 'manual'
    PAYMENT = 'payment'
    PAYMENT_PLAN = 'payment_plan'

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    payment = models.BooleanField()
    objects = CheckoutActionManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Checkout action'
        verbose_name_plural = 'Checkout action'

    def __str__(self):
        return '{}'.format(self.name)

    @property
    def invoice(self):
        return self.slug == self.INVOICE

reversion.register(CheckoutAction)


class CustomerManager(models.Manager):

    def _create_customer(self, name, email, customer_id):
        obj = self.model(name=name, email=email, customer_id=customer_id)
        obj.save()
        return obj

    def _get_customer(self, email):
        return self.model.objects.get(email=email)

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
        except (stripe.InvalidRequestError, stripe.StripeError) as e:
            raise CheckoutError(
                "Error creating Stripe customer '{}': {}".format(
                    email, _stripe_error(e)
            )) from e

    def _stripe_get_card_expiry(self, customer_id):
        result = (0, 0)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = stripe.Customer.retrieve(customer_id)
        default_card = customer['default_card']
        # find the details of the default card
        for card in customer['cards']['data']:
            if card['id'] == default_card:
                # find the expiry date of the default card
                result = (int(card['exp_year']), int(card['exp_month']))
                break
        return result

    def _stripe_update(self, customer_id, description, token):
        """Use the Stripe API to update a customer."""
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_customer = stripe.Customer.retrieve(customer_id)
            stripe_customer.description = description
            stripe_customer.card = token
            stripe_customer.save()
        except stripe.StripeError as e:
            raise CheckoutError(
                "Error updating Stripe customer '{}': {}".format(
                    customer_id, _stripe_error(e)
            )) from e

    def init_customer(self, content_object, token):
        """Initialise Stripe customer using email, description and token.

        1. Lookup existing customer record in the database.

           - Retrieve customer from Stripe and update description and token.

        2. If the customer does not exist:

          - Create Stripe customer with email, description and token.
          - Create a customer record in the database.

        Return the customer database record and clear the card ``refresh``
        flag.

        """
        name = content_object.checkout_name
        email = content_object.checkout_email
        try:
            obj = self._get_customer(email)
            obj.name = name
            obj.refresh = False
            obj.save()
            self._stripe_update(obj.customer_id, name, token)
        except self.model.DoesNotExist:
            customer_id = self._stripe_create(email, name, token)
            obj = self._create_customer(name, email, customer_id)
        return obj

    @property
    def refresh(self):
        return self.model.objects.filter(refresh=True)

    def refresh_credit_card(self, email):
        result = False
        try:
            customer = self._get_customer(email)
            result = customer.refresh
        except self.model.DoesNotExist:
            pass
        return result

    def update_card_expiry(self, email):
        """Find the customer, get the expiry date from Stripe and update."""
        try:
            obj = self._get_customer(email)
            year, month = self._stripe_get_card_expiry(obj.customer_id)
            if year and month:
                # last day of the month
                obj.expiry_date = date(year, month, 1) + relativedelta(
                    months=+1, day=1, days=-1
                )
                # is the card expiring soon?
                is_expiring = obj.is_expiring
                if obj.refresh == is_expiring:
                    pass
                else:
                    with transaction.atomic():
                        obj.refresh = is_expiring
                        # save the details
                        obj.save()
                        # email the customer
                        queue_mail_template(
                            obj,
                            self.model.MAIL_TEMPLATE_CARD_EXPIRY,
                            {obj.email: dict(name=obj.name)}
                        )
        except Customer.DoesNotExist:
            pass


class Customer(TimeStampedModel):
    """Stripe Customer.

    Link the Stripe customer to an email address (and name).

    Note: It is expected that multiple users in our databases could have the
    same email address.  If they have different names, then this table looks
    very confusing.  Try checking the 'content_object' of the 'Checkout' model
    if you need to diagnose an issue.

    """

    MAIL_TEMPLATE_CARD_EXPIRY = 'customer_card_expiry'

    name = models.TextField()
    email = models.EmailField(unique=True)
    customer_id = models.TextField()
    expiry_date = models.DateField(blank=True, null=True)
    refresh = models.BooleanField(
        default=False,
        help_text='Should the customer refresh their card details?'
    )
    objects = CustomerManager()

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return '{} {}'.format(self.email, self.customer_id)

    @property
    def is_expiring(self):
        """Is the card expiring within the next month?

        If the ``expiry_date`` is ``None``, then it has *not* expired.

        The expiry date is set to the last day of the month e.g. for September
        2015, the ``expiry_date`` will be 30/09/2015.

        """
        result = False
        one_month = date.today() + relativedelta(months=+1)
        if self.expiry_date and self.expiry_date <= one_month:
            return True
        return result
        #return bool(self.expiry_date and self.expiry_date < date.today())

reversion.register(Customer)


class CheckoutManager(models.Manager):

    def audit(self):
        return self.model.objects.all().order_by('-pk')

    def create_checkout(self, action, content_object, user):
        """Create a checkout payment request."""
        if action == CheckoutAction.objects.card_refresh:
            total = None
        else:
            total = content_object.checkout_total
        obj = self.model(
            checkout_date=timezone.now(),
            action=action,
            content_object=content_object,
            description=', '.join(content_object.checkout_description),
            total=total,
        )
        # an anonymous user can create a checkout
        if user.is_authenticated():
            obj.user = user
        obj.save()
        return obj

    def charge(self, content_object, current_user):
        """Collect some money from a customer.

        You must be a member of staff to use this method.  For payment plans,
        a background process will charge the card.  In this case, the user will
        be anonymous.

        We should only attempt to collect money if the customer has already
        entered their card details.

        """
        content_object.refresh_from_db()
        if not content_object.checkout_can_charge:
            raise CheckoutError('Cannot charge the card.')
        try:
            customer = Customer.objects.get(
                email=content_object.checkout_email
            )
        except Customer.DoesNotExist as e:
            raise CheckoutError(
                "Customer '{}' has not registered a card".format(
                    content_object.checkout_email
                )
            ) from e
        action = CheckoutAction.objects.charge
        checkout = self.create_checkout(
            action,
            content_object,
            current_user
        )
        checkout.customer = customer
        checkout.save()
        try:
            checkout.charge(current_user)
            with transaction.atomic():
                checkout.success()
        except CheckoutError:
            with transaction.atomic():
                checkout.fail()
                checkout.notify()

    def manual(self, content_object, current_user):
        """Mark a transaction as paid (manual).

        You must be a member of staff to use this method.

        """
        content_object.refresh_from_db()
        if not current_user.is_staff:
            raise CheckoutError(
                'Only a member of staff can mark this transaction as paid.'
            )
        valid_state = (
            CheckoutState.FAIL,
            CheckoutState.PENDING,
            CheckoutState.REQUEST,
        )
        if not content_object.state.slug in valid_state:
            raise CheckoutError('Cannot mark this transaction as paid.')
        action = CheckoutAction.objects.manual
        checkout = self.create_checkout(
            action,
            content_object,
            current_user
        )
        checkout.save()
        try:
            with transaction.atomic():
                checkout.success()
        except CheckoutError:
            with transaction.atomic():
                checkout.fail()

    def success(self):
        return self.audit().filter(state=CheckoutState.objects.success)


class Checkout(TimeStampedModel):
    """Checkout.

    Create a 'Checkout' instance when you want to interact with Stripe e.g.
    take a payment, get card details to set-up a payment plan or refresh the
    details of an expired card.

    """

    checkout_date = models.DateTimeField()
    action = models.ForeignKey(CheckoutAction)
    customer = models.ForeignKey(
        Customer,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='+',
        blank=True,
        null=True,
        help_text=(
            'User who created the checkout request '
            '(or blank if the the user is not logged in)'
        )
    )
    state = models.ForeignKey(
        CheckoutState,
        default=default_checkout_state
        #blank=True, null=True
    )
    description = models.TextField()
    total = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    # link to the object in the system which requested the checkout
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    objects = CheckoutManager()

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Checkout'
        verbose_name_plural = 'Checkouts'

    def __str__(self):
        return '{}'.format(self.content_object.checkout_email)

    def _charge(self):
        """Charge the card."""
        if self.action.payment:
            self._charge_stripe()

    def _charge_stripe(self):
        """Create the charge on stripe's servers."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            stripe.Charge.create(
                amount=as_pennies(self.total),
                currency=CURRENCY,
                customer=self.customer.customer_id,
                description=self.description,
            )
        except stripe.CardError as e:
            raise CheckoutError(
                "Card error: '{}' checkout '{}', object '{}': {}".format(
                    e.code, self.pk, self.content_object.pk, _card_error(e),
                )
            ) from e
        except stripe.StripeError as e:
            raise CheckoutError(
                "Card error: checkout '{}', object '{}': {}".format(
                    self.pk, self.content_object.pk, _stripe_error(e),
                )
            ) from e

    def _success_or_fail(self, state):
        self.state = state
        self.save()

    def charge(self, current_user):
        """Charge the user's card.

        Must be a member of staff or anonymous (used when running as a
        background task) to use this method.

        To take payments for the current user, use the ``charge_user`` method.

        """
        if current_user.is_staff or current_user.is_anonymous:
            self._charge()
        else:
            raise CheckoutError(
                "Cannot process - payments can only "
                "be taken by a member of staff. "
                "Current: '{}', Customer: '{}'".format(
                current_user.email, self.customer.email
            ))

    def charge_user(self, current_user):
        """Charge the card of the current user.

        Use this method when the logged in user is performing the transaction.

        To take money from another user's card, you must be a member of staff
        and use the ``charge`` method.

        """
        anonymous = not current_user.is_authenticated()
        if anonymous or self.customer.email == current_user.email:
            self._charge()
        else:
            raise CheckoutError(
                "Cannot process - payments can only be taken "
                "for an anonymous user or the current user. "
                "Current: '{}', Customer: '{}'".format(
                current_user.email, self.customer.email
            ))

    @property
    def content_object_url(self):
        return self.content_object.get_absolute_url()

    def fail(self):
        """Checkout failed - so update and notify admin."""
        self._success_or_fail(CheckoutState.objects.fail)
        return self.content_object.checkout_fail()

    @property
    def failed(self):
        """Did the checkout request fail?"""
        return self.state == CheckoutState.objects.fail

    @property
    def invoice_data(self):
        try:
            data = self.checkoutinvoice
            return filter(None, (
                data.contact_name,
                data.company_name,
                data.address_1,
                data.address_2,
                data.address_3,
                data.town,
                data.county,
                data.postcode,
                data.country,
                data.email,
                data.phone,
            ))
        except CheckoutAdditional.DoesNotExist:
            return []

    @property
    def is_invoice(self):
        return self.action == CheckoutAction.objects.invoice

    @property
    def is_manual(self):
        return self.action == CheckoutAction.objects.manual

    @property
    def is_payment(self):
        return self.action == CheckoutAction.objects.payment

    @property
    def is_payment_plan(self):
        """Used in success templates."""
        return self.action == CheckoutAction.objects.payment_plan

    def notify(self, request=None):
        """Send notification of checkout status.

        Pass in a 'request' if you want the email to contain the URL of the
        checkout transaction.

        """
        email_addresses = [n.email for n in Notify.objects.all()]
        if email_addresses:
            caption = self.action.name
            state = self.state.name
            subject = '{} - {} from {}'.format(
                state.upper(),
                caption.capitalize(),
                self.content_object.checkout_name,
            )
            message = '{} - {} - {} from {}, {}:'.format(
                self.created.strftime('%d/%m/%Y %H:%M'),
                state.upper(),
                caption,
                self.content_object.checkout_name,
                self.content_object.checkout_email,
            )
            message = message + '\n\n{}\n\n{}'.format(
                self.description,
                request.build_absolute_uri(self.content_object_url) if request else '',
            )
            queue_mail_message(
                self,
                email_addresses,
                subject,
                message,
            )
        else:
            logger.error(
                "Cannot send email notification of checkout transaction.  "
                "No email addresses set-up in 'enquiry.models.Notify'"
            )

    def success(self):
        """Checkout successful - so update and notify admin."""
        self._success_or_fail(CheckoutState.objects.success)
        return self.content_object.checkout_success(self)

reversion.register(Checkout)


class CheckoutAdditionalManager(models.Manager):

    def create_checkout_additional(self, checkout, **kwargs):
        obj = self.model(checkout=checkout, **kwargs)
        obj.save()
        return obj


class CheckoutAdditional(TimeStampedModel):
    """If a user decides to pay by invoice, there are the details.

    Links with the 'CheckoutForm' in ``checkout/forms.py``.  Probably easier to
    put validation in the form if required.

    """

    checkout = models.OneToOneField(Checkout)
    # company
    company_name = models.CharField(max_length=100, blank=True)
    address_1 = models.CharField('Address', max_length=100, blank=True)
    address_2 = models.CharField('', max_length=100, blank=True)
    address_3 = models.CharField('', max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    # contact
    contact_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=False)
    phone = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(}
    objects = CheckoutAdditionalManager()

    class Meta:
        ordering = ('email',)
        verbose_name = 'Checkout Additional Information'
        verbose_name_plural = 'Checkout Additional Information'

    def __str__(self):
        return '{}'.format(self.email)

reversion.register(CheckoutAdditional)


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

    def save(self, *args, **kwargs):
        if self.can_update:
            super().save(*args, **kwargs)
        else:
            raise CheckoutError(
                'Payment plan in use.  Cannot be updated.'
            )

    @property
    def can_update(self):
        count = ObjectPaymentPlan.objects.filter(payment_plan=self).count()
        if count:
            return False
        else:
            return True

    def deposit_amount(self, total):
        return (
            total * (self.deposit / Decimal('100'))
        ).quantize(Decimal('.01'))

    def instalments(self, deposit_due_date, total):
        # deposit
        deposit = self.deposit_amount(total)
        # list of dates
        first_interval = self.interval
        if deposit_due_date.day > 15:
            first_interval = first_interval + 1
        start_date = deposit_due_date + relativedelta(
            months=+first_interval,
            day=1,
        )
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

    def example(self, deposit_due_date, total):
        result = [
            (deposit_due_date, self.deposit_amount(total)),
        ]
        return result + self.instalments(deposit_due_date, total)

reversion.register(PaymentPlan)


class ObjectPaymentPlanManager(models.Manager):

    def charge_deposit(self, content_object, user):
        payment_plan = self.for_content_object(content_object)
        payment_plan.charge_deposit(user)

    def create_object_payment_plan(self, content_object, payment_plan, total):
        """Create a payment plan for an object with the initial deposit record.

        This method must be called from within a transaction.

        """
        obj = self.model(
            content_object=content_object,
            payment_plan=payment_plan,
            total=total,
        )
        obj.save()
        ObjectPaymentPlanInstalment.objects.create_object_payment_plan_instalment(
            obj,
            1,
            True,
            payment_plan.deposit_amount(total),
            date.today()
        )
        return obj

    def for_content_object(self, obj):
        return self.model.objects.get(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk
        )

    @property
    def outstanding_payment_plans(self):
        """List of outstanding payment plans.

        Used to refresh card expiry dates.

        """
        values = ObjectPaymentPlanInstalment.objects.filter(
            state__slug__in=(
                CheckoutState.FAIL,
                CheckoutState.PENDING,
                CheckoutState.REQUEST,
            ),
        ).values_list(
            'object_payment_plan__pk',
            flat=True
        )
        # 'set' will remove duplicate 'values'
        return self.model.objects.filter(
            pk__in=(set(values)),
        ).exclude(
            deleted=True,
        )

    @property
    def report_card_expiry_dates(self):
        emails = []
        result = []
        payment_plans = self.outstanding_payment_plans
        for item in payment_plans:
            emails.append(item.content_object.checkout_email)
        # get the expiry date for all the customers (as a 'dict')
        customers = dict(Customer.objects.filter(
            email__in=emails
        ).values_list(
            'email', 'expiry_date'
        ))
        for item in payment_plans:
            expiry_date = customers.get(item.content_object.checkout_email)
            result.append(dict(
                expiry_date=expiry_date,
                object_payment_plan=item,
            ))
        return sorted(result, key=expiry_date_as_str)

    def refresh_card_expiry_dates(self):
        """Refresh the card expiry dates for outstanding payment plans."""
        for plan in self.outstanding_payment_plans:
            Customer.objects.update_card_expiry(
                plan.content_object.checkout_email
            )


class ObjectPaymentPlan(TimeStampedModel):
    """Payment plan for an object."""


    # link to the object in the system which requested the payment plan
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    # payment plan
    payment_plan = models.ForeignKey(PaymentPlan)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    # is this object deleted?
    deleted = models.BooleanField(default=False)
    objects = ObjectPaymentPlanManager()

    class Meta:
        ordering = ('created',)
        unique_together = ('object_id', 'content_type')
        verbose_name = 'Object payment plan'
        verbose_name_plural = 'Object payment plans'

    def __str__(self):
        return '{} created {}'.format(self.payment_plan.name, self.created)

    @property
    def _check_create_instalments(self):
        """Check the current records to make sure we can create instalments."""
        instalments = self.objectpaymentplaninstalment_set.all()
        count = instalments.count()
        if not count:
            # a payment plan should always have a deposit record
            raise CheckoutError(
                "no deposit/instalment record set-up for "
                "payment plan: '{}'".format(self.pk)
            )
        if count == 1:
            # check the first payment is the deposit
            first_instalment = instalments.first()
            if first_instalment.deposit:
                deposit_due_date = first_instalment.due
            else:
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
        return deposit_due_date

    def create_instalments(self):
        deposit_due_date = self._check_create_instalments
        instalments = self.payment_plan.instalments(
            deposit_due_date,
            self.total
        )
        count = 1
        for due, amount in instalments:
            count = count + 1
            ObjectPaymentPlanInstalment.objects.create_object_payment_plan_instalment(
                self,
                count,
                False,
                amount,
                due,
            )

    def charge_deposit(self, user):
        self._check_create_instalments
        deposit = self.objectpaymentplaninstalment_set.first()
        Checkout.objects.charge(deposit, user)

    @property
    def payment_count(self):
        return self.objectpaymentplaninstalment_set.count()

    @property
    def payments(self):
        return self.objectpaymentplaninstalment_set.all().order_by('count')

reversion.register(ObjectPaymentPlan)


class ObjectPaymentPlanInstalmentManager(models.Manager):

    #@property
    #def checkout_list(self):
    #    """All 'checkout' transactions for object payment plan instalments.
    #    Use to audit checkout failures so we can block access.
    #    """
    #    return Checkout.objects.filter(
    #        content_type=ContentType.objects.get_for_model(self.model),
    #    )

    def create_object_payment_plan_instalment(
            self, object_payment_plan, count, deposit, amount, due):
        obj = self.model(
            object_payment_plan=object_payment_plan,
            count=count,
            deposit=deposit,
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
            due__lte=date.today(),
            state__slug=CheckoutState.PENDING,
        ).exclude(
            deposit=True,
        ).exclude(
            object_payment_plan__deleted=True,
        )

    def process_payments(self):
        """Process pending payments.

        We set the status to 'request' before asking for the money.  This is
        because we can't put the payment request into a transaction.  If we are
        not careful, we could have a situation where the payment succeeds and
        we don't manage to set the state to 'success'.  In the code below, if
        the payment fails the record will be left in the 'request' state and
        so we won't ask for the money again.

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
            Checkout.objects.charge(instalment, AnonymousUser())


class ObjectPaymentPlanInstalment(TimeStampedModel):
    """Payments due for an object.

    The deposit record gets created first.  It has the ``deposit`` field set to
    ``True``.

    The instalment records are created after the deposit has been collected.
    Instalment records have the ``deposit`` field set to ``False``.

    """

    object_payment_plan = models.ForeignKey(ObjectPaymentPlan)
    count = models.IntegerField()
    state = models.ForeignKey(
        CheckoutState,
        default=default_checkout_state,
        #blank=True, null=True
    )
    deposit = models.BooleanField(help_text='Is this the initial payment')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    due = models.DateField()
    objects = ObjectPaymentPlanInstalmentManager()

    class Meta:
        unique_together = (
            ('object_payment_plan', 'due'),
            ('object_payment_plan', 'count'),
        )
        verbose_name = 'Payments for an object'
        verbose_name_plural = 'Payments for an object'

    def __str__(self):
        return '{} {} {}'.format(
            self.object_payment_plan.payment_plan.name,
            self.due,
            self.amount,
        )

    def get_absolute_url(self):
        """TODO Update this to display the payment plan."""
        return reverse('project.home')

    @property
    def checkout_actions(self):
        """No actions as payment is charged directly."""
        return []

    @property
    def checkout_can_charge(self):
        """Check we can take the payment."""
        result = False
        if self.deposit:
            check = self.state.slug == CheckoutState.PENDING
        else:
            check = self.state.slug == CheckoutState.REQUEST
        if check:
            result = self.due <= date.today()
        return result

    @property
    def checkout_description(self):
        result = [
            '{}'.format(
                self.object_payment_plan.payment_plan.name,
            ),
        ]
        if self.deposit:
            result.append('Deposit')
        else:
            result.append('Instalment {} of {}'.format(
                self.count,
                self.object_payment_plan.payment_count,
            ))
        return result

    @property
    def checkout_email(self):
        return self.object_payment_plan.content_object.checkout_email

    def checkout_fail(self):
        """Update the object to record the payment failure.

        Called from within a transaction so you can update the model.

        """
        self.state = CheckoutState.objects.fail
        self.save()
        self.object_payment_plan.content_object.checkout_fail(due=self.due)

    def checkout_fail_url(self, checkout_pk):
        """No UI, so no URL."""
        return None

    @property
    def checkout_name(self):
        return self.object_payment_plan.content_object.checkout_name

    def checkout_success(self, checkout):
        """Update the object to record the payment success.

        Called from within a transaction and you can update the model.

        """
        self.state = checkout.state
        self.save()
        if self.deposit:
            self.object_payment_plan.create_instalments()
        self.object_payment_plan.content_object.checkout_success(checkout)

    def checkout_success_url(self, checkout_pk):
        """No UI, so no URL."""
        return None

    @property
    def checkout_total(self):
        return self.amount

reversion.register(ObjectPaymentPlanInstalment)


class CheckoutSettingsManager(models.Manager):

    @property
    def settings(self):
        try:
            return self.model.objects.get()
        except self.model.DoesNotExist:
            raise CheckoutError(
                "Checkout settings have not been set-up in admin"
            )


class CheckoutSettings(SingletonModel):

    default_payment_plan = models.ForeignKey(
        PaymentPlan,
    )
    objects = CheckoutSettingsManager()

    class Meta:
        verbose_name = 'Checkout Settings'

    def __str__(self):
        return "Default Payment Plan: {}".format(
            self.default_payment_plan.name
        )

reversion.register(CheckoutSettings)


#class ObjectPaymentPlanInstalmentCheckoutAudit(TimeStampedModel):
#    """Keep an audit of checkout status."""
#
#    object_payment_plan_instalment = models.ForeignKey(
#        ObjectPaymentPlanInstalment
#    )
#    state = models.ForeignKey(
#        CheckoutState,
#        default=default_checkout_state,
#        #blank=True, null=True
#    )
#
#                ChargeAudit.objects.create_charge_audit(
#                    content_object,
#                    current_user,
#                    checkout,
#                )
