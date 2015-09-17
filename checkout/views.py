# -*- encoding: utf-8 -*-
import json
import logging

from datetime import date

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils import timezone
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
    ObjectPaymentPlanEmptyForm,
    ObjectPaymentPlanInstalmentEmptyForm,
    PaymentPlanEmptyForm,
    PaymentPlanForm,
)
from .models import (
    as_pennies,
    Checkout,
    CheckoutAction,
    CheckoutError,
    CheckoutInvoice,
    CheckoutSettings,
    CURRENCY,
    Customer,
    ObjectPaymentPlan,
    ObjectPaymentPlanInstalment,
    PaymentPlan,
)


CONTENT_OBJECT_PK = 'content_object_pk'
logger = logging.getLogger(__name__)


def _check_perm(request, content_object):
    """Check the session variable to make sure it was set."""
    pk = request.session.get(CONTENT_OBJECT_PK, None)
    if pk:
        pk = int(pk)
        if not pk == content_object.pk:
            logger.critical(
                'content object check: invalid: {} != {}'.format(
                    pk, content_object.pk,
                )
            )
            raise PermissionDenied('content check failed')
    else:
        logger.critical('content object check: invalid')
        raise PermissionDenied('content check failed')


def _check_perm_success(request, payment):
    """Check the permissions for the checkout success (thank you) page.

    We check the user (who might be anonymous) is not viewing an old
    transaction.

    """
    _check_perm(request, payment.content_object)
    td = timezone.now() - payment.created
    diff = td.days * 1440 + td.seconds / 60
    if abs(diff) > 10:
        raise CheckoutError(
            "Cannot view this checkout transaction.  It is too old "
            "(or has travelled in time, {} {} {}).".format(
                payment.created.strftime('%d/%m/%Y %H:%M'),
                timezone.now().strftime('%d/%m/%Y %H:%M'),
                abs(diff),
            )
        )


def payment_plan_example(total):
    checkout_settings = CheckoutSettings.objects.settings
    payment_plan = checkout_settings.default_payment_plan
    return payment_plan.example(date.today(), total)


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


class CheckoutCardRefreshListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    paginate_by = 10
    template_name = 'checkout/card_refresh_list.html'

    def get_queryset(self):
        return Customer.objects.refresh


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
    """Checkout.

    Use with an ``UpdateView`` e.g::

      class ShopCheckoutUpdateView(CheckoutMixin, BaseMixin, UpdateView):

    """

    def _action_data(self):
        """the action data for the javascript on the page."""
        actions = self.object.checkout_actions
        result = {}
        for slug in actions:
            obj = CheckoutAction.objects.get(slug=slug)
            result[slug] = dict(
                name=obj.name,
                payment=obj.payment,
            )
        return json.dumps(result)

    def _form_valid_invoice(self, checkout, form):
        data = form.invoice_data()
        CheckoutInvoice.objects.create_checkout_invoice(checkout, **data)

    def _form_valid_stripe(self, checkout, token):
        customer = Customer.objects.init_customer(self.object, token)
        checkout.customer = customer
        checkout.save()
        checkout.charge_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _check_perm(self.request, self.object)
        if not self.object.checkout_can_charge:
            raise CheckoutError('Cannot charge: {}'.format(str(self.object)))
        checkout_actions = self.object.checkout_actions
        context.update(dict(
            action_data=self._action_data(),
            allow_pay_by_invoice=CheckoutAction.INVOICE in checkout_actions,
            currency=CURRENCY,
            description=self.object.checkout_description,
            email=self.object.checkout_email,
            key=settings.STRIPE_PUBLISH_KEY,
            name=settings.STRIPE_CAPTION,
            total=as_pennies(self.object.checkout_total), # pennies
        ))
        if CheckoutAction.PAYMENT_PLAN in checkout_actions:
            context.update(dict(
                example=payment_plan_example(self.object.checkout_total),
            ))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(dict(actions=self.object.checkout_actions))
        return kwargs

    #def form_invalid(self, form):
    #    import ipdb
    #    ipdb.set_trace()
    #    print(form.errors)
    #    logger.error(form.errors)

    def form_valid(self, form):
        """Process the payment.

        Note: We do NOT update 'self.object'

        """
        self.object = form.save(commit=False)
        token = form.cleaned_data['token']
        slug = form.cleaned_data['action']
        action = CheckoutAction.objects.get(slug=slug)
        checkout = None
        try:
            with transaction.atomic():
                checkout = Checkout.objects.create_checkout(
                    action, self.object, self.request.user
                )
            # do stripe stuff outside of a transaction so we have some chance
            # of diagnosing progress if an exception is thrown.
            if not action.invoice:
                if not token:
                    raise CheckoutError(
                        "No checkout 'token' for: '{}'".format(self.object)
                    )
                self._form_valid_stripe(checkout, token)
            with transaction.atomic():
                if action.invoice:
                    self._form_valid_invoice(checkout, form)
                checkout.success()
                checkout.notify(self.request)
            url = self.object.checkout_success_url(checkout.pk)
            process_mail.delay()
        except CheckoutError as e:
            logger.error(e)
            if checkout:
                with transaction.atomic():
                    checkout.fail()
            url = self.object.checkout_fail_url(checkout.pk)
            # PJK TODO remove temp
            raise
        return HttpResponseRedirect(url)


class CheckoutSuccessMixin(object):
    """Thank you for your payment (etc).

    Use with a ``DetailView`` e.g::

      class ShopCheckoutSuccessView(
          CheckoutSuccessMixin, BaseMixin, DetailView):

    """

    model = Checkout

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _check_perm_success(self.request, self.object)
        if self.object.action == CheckoutAction.objects.payment_plan:
            context.update(example=payment_plan_example(self.object.total))
        return context


class ObjectPaymentPlanDeleteView(
        LoginRequiredMixin, StaffuserRequiredMixin, BaseMixin, UpdateView):

    form_class = ObjectPaymentPlanEmptyForm
    model = ObjectPaymentPlan
    template_name = 'checkout/object_paymentplan_delete.html'

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.deleted = True
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('checkout.object.payment.plan.list')


class ObjectPaymentPlanListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    model = ObjectPaymentPlan
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(allow_manual_payment=True))
        return context

    def get_queryset(self):
        return ObjectPaymentPlan.objects.outstanding_payment_plans


class ObjectPaymentPlanCardExpiryListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    paginate_by = 10
    template_name = 'checkout/card_expiry_list.html'

    def get_queryset(self):
        return ObjectPaymentPlan.objects.report_card_expiry_dates


class ObjectPaymentPlanInstalmentDetailView(
        StaffuserRequiredMixin, LoginRequiredMixin, BaseMixin, DetailView):

    model = ObjectPaymentPlanInstalment


class ObjectPaymentPlanInstalmentPaidUpdateView(
        StaffuserRequiredMixin, LoginRequiredMixin, BaseMixin, UpdateView):
    """Mark this instalment as paid."""

    model = ObjectPaymentPlanInstalment
    form_class = ObjectPaymentPlanInstalmentEmptyForm

    def form_valid(self, form):
        Checkout.objects.manual(self.object, self.request.user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'checkout.object.payment.plan.instalment',
            args=[self.object.pk]
        )


#class ObjectPaymentPlanInstalmentChargeUpdateView(
#        StaffuserRequiredMixin, LoginRequiredMixin, BaseMixin, UpdateView):
#    """Charge the customer's card for this instalment."""
#
#    model = ObjectPaymentPlanInstalment
#    form_class = ObjectPaymentPlanInstalmentEmptyForm
#
#    def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        if not self.object.checkout_can_charge:
#            messages.warning(
#                self.request, 'Payment cannot be taken for this instalment.'
#            )
#        return context
#
#    def form_valid(self, form):
#        """Replace this code with ``ObjectPaymentPlan.charge_deposit``."""
#        Checkout.objects.charge(self.object, self.request.user)
#        if self.object.deposit:
#            with transaction.atomic():
#                self.object.object_payment_plan.create_instalments()
#        return HttpResponseRedirect(self.get_success_url())
#
#    def get_success_url(self):
#        return reverse(
#            'checkout.object.payment.plan.instalment',
#            args=[self.object.pk]
#        )


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
