# -*- encoding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    UpdateView,
    RedirectView,
    TemplateView,
)

from braces.views import LoginRequiredMixin

from base.view_utils import BaseMixin
from checkout.models import (
    Checkout,
    ObjectPaymentPlan,
)
from checkout.views import (
    CheckoutMixin,
    CheckoutThankyouMixin,
    CONTENT_OBJECT_PK,
)
from .forms import (
    EmptyForm,
    SalesLedgerCheckoutForm,
    SalesLedgerEmptyForm,
)
from .models import SalesLedger


class ExampleRefreshExpiryDatesFormView(FormView):

    form_class = EmptyForm
    template_name = 'example/refresh_expiry_dates.html'

    def form_valid(self, form):
        ObjectPaymentPlan.objects.refresh_card_expiry_dates()
        messages.success(self.request, 'Completed card refresh at {}'.format(
            timezone.now().strftime('%H:%M:%S on the %d/%m/%Y')
        ))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('example.refresh.card.expiry.dates')


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


class SalesLedgerCheckoutView(CheckoutMixin, BaseMixin, UpdateView):
    """A charge can be made by the logged in user or an anonymous user."""

    model = SalesLedger
    form_class = SalesLedgerCheckoutForm
    template_name = 'example/checkout.html'


class SalesLedgerSessionRedirectView(RedirectView):
    """Set session variable so permission checks pass in checkout."""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs['pk']
        self.request.session[CONTENT_OBJECT_PK] = pk
        return reverse('example.sales.ledger.checkout', args=[pk])


class SalesLedgerCheckoutThankyouView(
          CheckoutThankyouMixin, BaseMixin, DetailView):

    template_name = 'example/checkout_thankyou.html'


class SettingsView(BaseMixin, TemplateView):

    template_name = 'example/settings.html'
