# -*- encoding: utf-8 -*-
import logging
import stripe

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
#from django.views.decorators.http import require_POST
from django.views.generic import ListView

from braces.views import (
    LoginRequiredMixin,
    StaffuserRequiredMixin,
)

from base.view_utils import BaseMixin
from mail.models import Notify
from mail.service import (
    queue_mail_message,
    queue_mail_template,
)
from mail.tasks import process_mail

from .forms import CheckoutForm
from .models import (
    Checkout,
    Customer,
    log_stripe_error,
)
#from .service import (
#    PAYMENT_LATER,
#    PAYMENT_THANKYOU,
#)


CURRENCY = 'GBP'
CHECKOUT_PK = 'payment_pk'

logger = logging.getLogger(__name__)

#class PayPalFormView(LoginRequiredMixin, BaseMixin, FormView):
#
#    form_class = PayPalPaymentsForm
#    template_name = 'pay/paypal.html'
#
#    def get_initial(self):
#        return dict(
#            business=settings.PAYPAL_RECEIVER_EMAIL,
#            amount='10.01',
#            currency_code='GBP',
#            item_name='Cycle Routes around Hatherleigh',
#            invoice='0001',
#            notify_url="https://www.example.com" + reverse('paypal-ipn'),
#            return_url="https://www.example.com/your-return-location/",
#            cancel_return="https://www.example.com/your-cancel-location/",
#        )


def _check_perm(request, payment):
    """Check the session variable to make sure it was set."""
    payment_pk = request.session.get(CHECKOUT_PK, None)
    if payment_pk:
        if not payment_pk == payment.pk:
            logger.critical(
                'payment check: invalid {} != {}'.format(
                    payment_pk, payment.pk,
            ))
            raise PermissionDenied('Valid payment check fail.')
    else:
        logger.critical('payment check: invalid')
        raise PermissionDenied('Valid payment check failed.')


def _log_card_error(e, payment_pk):
    logger.error(
        'CardError\n'
        'payment: {}\n'
        'param: {}\n'
        'code: {}\n'
        'http body: {}\n'
        'http status: {}'.format(
            payment_pk,
            e.param,
            e.code,
            e.http_body,
            e.http_status,
        )
    )


def _notify_admin(checkout, description, request):
    email_addresses = [n.email for n in Notify.objects.all()]
    if email_addresses:
        subject, message = payment.mail_subject_and_message(request)
        caption = checkout.action.name
        subject = '{} from {}'.format(caption.capitalize(), checkout.customer.name)
        message = '{} - {} from {}, {}:'.format(
            self.created.strftime('%d/%m/%Y %H:%M'),
            caption,
            checkout.customer.name,
            checkout.customer.email,
        )
        message = message + '\n\n{}\n\n{}'.format(
            description,
            request.build_absolute_uri(self.content_object.get_absolute_url()),
        )
        queue_mail_message(
            payment,
            email_addresses,
            subject,
            message,
        )
    else:
        logging.error(
            "Cannot send email notification of payment.  "
            "No email addresses set-up in 'enquiry.models.Notify'"
        )


#@require_POST
#def pay_later_view(request, pk):
#    payment = Payment.objects.get(pk=pk)
#    _check_perm(request, payment)
#    payment.check_can_pay
#    payment.set_pay_later()
#    queue_mail_template(
#        payment,
#        payment.mail_template_name,
#        payment.mail_template_context(),
#    )
#    _send_notification_email(payment, request)
#    process_mail.delay()
#    return HttpResponseRedirect(payment.url)


class PaymentAuditListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(audit=True))
        return context

    def get_queryset(self):
        return Checkout.objects.audit()


class PaymentListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(audit=False))
        return context

    def get_queryset(self):
        return Checkout.objects.payments()


class StripeMixin(object):

    #form_class = CheckoutForm
    #model = Checkout

    def _init_customer(self, email, description, token):
        """Make sure a stripe customer is created and update card (token)."""
        return Customer.objects.init_customer(email, description, token)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO PJK Do I need to re-instate this?
        # _check_perm(self.request, self.object)
        # self.object.check_can_pay
        context.update(dict(
            currency=CURRENCY,
            description=self.object.checkout_description,
            email=self.object.checkout_email,
            key=settings.STRIPE_PUBLISH_KEY,
            name=settings.STRIPE_CAPTION,
            total=self.as_pennies(self.object.checkout_total), # pennies
        ))
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # Create the charge on Stripe's servers - this will charge the users card
        token = form.cleaned_data['token']
        # self.object.save_token(token)
        # Set your secret key: remember to change this to your live secret key
        # in production.  See your keys here https://manage.stripe.com/account
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # create a checkout request
            # checkout = self.object.checkout(token)
            checkout = self.object.create_checkout(
                self.object.checkout_name,
                self.object.checkout_email,
                token,
                self.object,
            )

            # checkout.token = token
            # checkout.save()
            # # initialise the customer
            # customer = self._init_customer(
            #     checkout.email,
            #     checkout.description,
            #     token
            # )
            description = ', '.join(self.object.checkout_description)
            if checkout.payment:
                checkout.total = self.object.checkout_total
                checkout.save()
                stripe.Charge.create(
                    amount=self.as_pennies(checkout.total), # pennies
                    currency=CURRENCY,
                    customer=checkout.customer.customer_id,
                    description=description,
                )
            with transaction.atomic():
                #self.object.set_checkout_state(CheckoutState.objects.success)
                checkout.success
                url = self.object.checkout_success
                _notify_admin(checkout, description, self.request)
            # this should now be done by the object in 'checkout_success'
            # queue_mail_template(
            #     self.object,
            #     self.object.mail_template_name,
            #     self.object.mail_template_context(),
            # )
            process_mail.delay()
            result = super().form_valid(form)
        except stripe.CardError as e:
            url = self.object.checkout_failure
            # self.object.set_payment_failed()
            _log_card_error(e, self.object.pk)
            result = HttpResponseRedirect(url)
        except stripe.StripeError as e:
            url = self.object.checkout_failure
            # self.object.set_payment_failed()
            log_stripe_error(logger, e, 'payment: {}'.format(self.object.pk))
            result = HttpResponseRedirect(url)
        return result

    def get_success_url(self):
        return self.object.url

    def as_pennies(self, total):
        return int(total * Decimal('100'))
