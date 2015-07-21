# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import (
    ListView,
    UpdateView,
)

from braces.views import LoginRequiredMixin

from base.view_utils import BaseMixin
from checkout.models import Checkout
from checkout.views import CheckoutMixin
from .forms import (
    SalesLedgerCheckoutForm,
    SalesLedgerEmptyForm,
)
from .models import SalesLedger


class HomeView(ListView):

    model = SalesLedger
    template_name = 'example/home.html'


class SalesLedgerChargeUpdateView(
        LoginRequiredMixin, BaseMixin, UpdateView):

    model = SalesLedger
    form_class = SalesLedgerEmptyForm
    template_name = 'example/charge.html'

    def form_valid(self, form):
        Checkout.objects.charge(self.object, self.request.user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('checkout.list.audit')


class SalesLedgerCheckoutUpdateView(
        LoginRequiredMixin, CheckoutMixin, BaseMixin, UpdateView):

    model = SalesLedger
    form_class = SalesLedgerCheckoutForm
    template_name = 'example/checkout.html'
