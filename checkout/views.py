# -*- encoding: utf-8 -*-
import json
import logging
import stripe

from django.conf import settings
from django.contrib import messages
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
    ObjectPaymentPlanInstalmentEmptyForm,
    PaymentPlanEmptyForm,
    PaymentPlanForm,
)
from .models import (
    as_pennies,
    Checkout,
    CheckoutAction,
    CheckoutError,
    ObjectPaymentPlan,
    ObjectPaymentPlanInstalment,
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

    #def _checkout_fail(self):
    #    I don't know if we need this method
    #    return self.object.checkout_fail()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO PJK Do I need to re-instate this?
        # _check_perm(self.request, self.object)
        # self.object.check_can_pay
        context.update(dict(
            action_data=self._action_data(),
            currency=CURRENCY,
            description=self.object.checkout_description,
            email=self.object.checkout_email,
            key=settings.STRIPE_PUBLISH_KEY,
            name=settings.STRIPE_CAPTION,
            total=as_pennies(self.object.checkout_total), # pennies
        ))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(dict(
            #actions=[CheckoutAction.PAYMENT, CheckoutAction.PAYMENT_PLAN],
            #actions=[CheckoutAction.PAYMENT_PLAN],
            actions=self.object.checkout_actions,
        ))
        return kwargs

    def form_valid(self, form):
        """

        TODO PJK This view is trying to update the model in the standard form
        update view way (``form.save()``) and is also trying to process the
        payment on the model.  I think it would be better if we didn't do the
        standard form save, but just processed the payment.  This would be
        similar to the way we use the ``UpdateView`` for deleting models.

        """
        self.object = form.save(commit=False)
        checkout = None
        token = form.cleaned_data['token']
        slug = form.cleaned_data['action']
        action = CheckoutAction.objects.get(slug=slug)
        customer = Customer.objects.init_customer(self.object, token)
        checkout = Checkout.objects.create_checkout(
            action, self.object, customer, self.request.user
        )
        try:
            checkout.process()
            with transaction.atomic():
                #self.object = form.save()
                checkout.success()
                checkout.notify(self.request)
            url = self.object.checkout_success_url
            process_mail.delay()
        except CheckoutError:
            with transaction.atomic():
                checkout.fail()
            url = self.object.checkout_fail_url
        except stripe.StripeError as e:
            # TODO Move the exception handling into the model and just throw (and catch) a new 'CheckoutFail' exception.
            log_stripe_error(logger, e, 'checkout: {} content_object: {}'.format(
                checkout.pk if checkout else None,
                self.object.pk
            ))
            with transaction.atomic():
                checkout.fail()
            url = self.object.checkout_fail_url
        return HttpResponseRedirect(url)


class ObjectPaymentPlanListView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        BaseMixin, ListView):

    model = ObjectPaymentPlan
    paginate_by = 10


class ObjectPaymentPlanInstalmentDetailView(
        StaffuserRequiredMixin, LoginRequiredMixin, BaseMixin, DetailView):

    model = ObjectPaymentPlanInstalment


class ObjectPaymentPlanInstalmentChargeUpdateView(
        StaffuserRequiredMixin, LoginRequiredMixin, BaseMixin, UpdateView):
    """Charge the customer's card for this instalment."""

    model = ObjectPaymentPlanInstalment
    form_class = ObjectPaymentPlanInstalmentEmptyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.checkout_can_charge:
            messages.warning(
                self.request, 'Payment cannot be taken for this instalment.'
            )
        return context

    def form_valid(self, form):
        Checkout.objects.charge(self.object, self.request.user)
        if self.object.deposit:
            with transaction.atomic():
                self.object.object_payment_plan.create_instalments()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'checkout.object.payment.plan.instalment',
            args=[self.object.pk]
        )


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
