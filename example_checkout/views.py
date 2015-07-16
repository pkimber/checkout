# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse
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
)
from checkout.views import CheckoutMixin
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
        Checkout.objects.direct_debit(self.request.user, self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('checkout.list.audit')


class SalesLedgerCheckoutUpdateView(
        LoginRequiredMixin, CheckoutMixin, BaseMixin, UpdateView):

    model = SalesLedger
    form_class = SalesLedgerCheckoutForm
    template_name = 'example/checkout.html'
