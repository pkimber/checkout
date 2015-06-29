# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic import (
    ListView,
    UpdateView,
)

from braces.views import LoginRequiredMixin

from base.view_utils import BaseMixin
from checkout.models import (
    Checkout,
    CheckoutAction,
    Customer,
)
from checkout.views import (
    CHECKOUT_PK,
    CheckoutMixin,
)
from .forms import (
    SalesLedgerCheckoutForm,
    SalesLedgerEmptyForm,
)
from .models import SalesLedger


class HomeView(ListView):

    model = SalesLedger
    template_name = 'example/home.html'


class SalesLedgerCheckoutDirectDebitUpdateView(
        LoginRequiredMixin, BaseMixin, UpdateView):

    model = SalesLedger
    form_class = SalesLedgerEmptyForm
    template_name = 'example/direct_debit.html'

    def form_valid(self, form):
        customer = Customer.objects.get(email=self.object.checkout_email)
        checkout = Checkout.objects.pay(
            CheckoutAction.objects.payment,
            customer,
            self.object
        )
        with transaction.atomic():
            checkout.success(self.request)
            self.object.checkout_success(checkout)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('checkout.list.audit')


class SalesLedgerCheckoutUpdateView(
        LoginRequiredMixin, CheckoutMixin, BaseMixin, UpdateView):

    model = SalesLedger
    form_class = SalesLedgerCheckoutForm
    template_name = 'example/checkout.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(dict(
            actions=[CheckoutAction.PAYMENT, CheckoutAction.PAYMENT_PLAN],
            #actions=[CheckoutAction.PAYMENT_PLAN],
        ))
        return kwargs
