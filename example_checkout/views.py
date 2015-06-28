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
from checkout.views import (
    CHECKOUT_PK,
    StripeMixin,
)
from .forms import ExampleCheckoutForm
from .models import SalesLedger


class HomeView(ListView):

    model = SalesLedger
    template_name = 'example/home.html'


class SalesLedgerCheckoutUpdateView(
        LoginRequiredMixin, StripeMixin, BaseMixin, UpdateView):

    model = SalesLedger
    form_class = ExampleCheckoutForm
    template_name = 'example/stripe.html'
