# -*- encoding: utf-8 -*-
import logging
import stripe

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic import ListView

from braces.views import (
    LoginRequiredMixin,
    StaffuserRequiredMixin,
)

from base.view_utils import BaseMixin
from mail.tasks import process_mail

from .models import (
    Checkout,
    CheckoutAction,
    Customer,
    log_stripe_error,
)


CURRENCY = 'GBP'
CHECKOUT_PK = 'payment_pk'

logger = logging.getLogger(__name__)


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


def _log_card_error(e, checkout_pk, content_object_pk):
    logger.error(
        'CardError\n'
        'checkout: {}\n'
        'content_object: {}\n'
        'param: {}\n'
        'code: {}\n'
        'http body: {}\n'
        'http status: {}'.format(
            checkout_pk,
            content_object_pk,
            e.param,
            e.code,
            e.http_body,
            e.http_status,
        )
    )


class CheckoutAuditListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(audit=True))
        return context

    def get_queryset(self):
        return Checkout.objects.audit()


class CheckoutListView(
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
        checkout = None
        token = form.cleaned_data['token']
        action = CheckoutAction.objects.payment
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout = Checkout.objects.create_checkout(
                action=action,
                name=self.object.checkout_name,
                email=self.object.checkout_email,
                description=', '.join(self.object.checkout_description),
                token=token,
                content_object=self.object,
            )
            if checkout.payment:
                checkout.total = self.object.checkout_total
                checkout.save()
                # Create the charge on stripe's servers
                stripe.Charge.create(
                    amount=self.as_pennies(checkout.total), # pennies
                    currency=CURRENCY,
                    customer=checkout.customer.customer_id,
                    description=checkout.description,
                )
            with transaction.atomic():
                url = checkout.success(self.request)
            process_mail.delay()
            self.object = form.save()
            return HttpResponseRedirect(url)
        except stripe.CardError as e:
            _log_card_error(e, checkout.pk if checkout else None, self.object.pk)
            url = checkout.fail(self.request)
            result = HttpResponseRedirect(url)
        except stripe.StripeError as e:
            message = 'checkout: {} content_object: {}'.format(
                checkout.pk if checkout else None,
                self.object.pk
            )
            log_stripe_error(logger, e, message)
            url = checkout.fail(self.request)
            result = HttpResponseRedirect(url)
        return result

    def as_pennies(self, total):
        return int(total * Decimal('100'))
