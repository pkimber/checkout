# -*- encoding: utf-8 -*-
import logging
import stripe

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from braces.views import (
    LoginRequiredMixin,
    StaffuserRequiredMixin,
)

from base.view_utils import BaseMixin
from mail.tasks import process_mail

from .forms import (
    PaymentPlanEmptyForm,
    PaymentPlanForm,
)
from .models import (
    as_pennies,
    Checkout,
    CheckoutAction,
    ContactPlan,
    CURRENCY,
    Customer,
    log_stripe_error,
    PaymentPlan,
)


CHECKOUT_PK = 'checkout_pk'
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
        return Checkout.objects.success()


class CheckoutMixin(object):

    def _checkout_fail(self):
            return self.object.checkout_fail()

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
            total=as_pennies(self.object.checkout_total), # pennies
        ))
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        checkout = None
        token = form.cleaned_data['token']
        slug = form.cleaned_data['action']
        action = CheckoutAction.objects.get(slug=slug)
        try:
            customer = Customer.objects.init_customer(self.object, token)
            checkout = Checkout.objects.pay(action, customer, self.object)
            with transaction.atomic():
                self.object = form.save()
                checkout.success()
                checkout.notify(self.request)
            url = self.object.checkout_success_url
            process_mail.delay()
        except stripe.CardError as e:
            # TODO Move the exception handling into the model and just throw (and catch) a new 'CheckoutFail' exception.
            _log_card_error(e, checkout.pk if checkout else None, self.object.pk)
            with transaction.atomic():
                checkout.fail()
            url = self.object.fail_url
        except stripe.StripeError as e:
            # TODO Move the exception handling into the model and just throw (and catch) a new 'CheckoutFail' exception.
            log_stripe_error(logger, e, 'checkout: {} content_object: {}'.format(
                checkout.pk if checkout else None,
                self.object.pk
            ))
            with transaction.atomic():
                checkout.fail()
            url = self.object.fail_url
        return HttpResponseRedirect(url)


class ContactPlanListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    model = ContactPlan
    paginate_by = 10


class PaymentPlanCreateView(
        LoginRequiredMixin, StaffuserRequiredMixin, BaseMixin, CreateView):

    form_class = PaymentPlanForm
    model = PaymentPlan

    def get_success_url(self):
        return reverse('checkout.payment.plan.list')


class PaymentPlanDeleteView(
        LoginRequiredMixin, StaffuserRequiredMixin, BaseMixin, UpdateView):

    form_class = PaymentPlanEmptyForm
    model = PaymentPlan
    template_name = 'checkout/paymentplan_delete.html'

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.deleted = True
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('checkout.payment.plan.list')


class PaymentPlanListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    paginate_by = 5

    def get_queryset(self):
        return PaymentPlan.objects.current()


class PaymentPlanUpdateView(
        LoginRequiredMixin, StaffuserRequiredMixin, BaseMixin, UpdateView):

    form_class = PaymentPlanForm
    model = PaymentPlan

    def get_success_url(self):
        return reverse('checkout.payment.plan.list')
