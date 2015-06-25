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
    PAYMENT_PK,
    StripeMixin,
)
from .forms import ExampleCheckoutForm
from .models import SalesLedger


class ExampleCheckout(StripeMixin, BaseMixin, UpdateView):
    """When the user does an HTTP POST to this view, create and attach a
    payment record to the sales ledger item so it can be paid.

    """

    model = SalesLedger
    form_class = ExampleCheckoutForm
    template_name = 'example/salesledger_form.html'

    def form_valid(self, form):
        with transaction.atomic():
            super(ExampleCheckout, self).form_valid(form)
            payment = self.object.create_payment()
            payment.url = reverse('pay.list')
            payment.url_failure = reverse('pay.list')
            payment.save()
            self.request.session[PAYMENT_PK] = payment.pk
            return HttpResponseRedirect(
                reverse('example.pay.stripe', kwargs=dict(pk=payment.pk))
            )

    def get_success_url(self):
        """called by 'form_valid' (above) but the result is not used."""
        return reverse('project.home')


#class ExamplePaymentDetailView(DetailView):
#
#    template_name = 'example_pay/payment_detail.html'
#    model = Payment


class HomeView(ListView):

    model = SalesLedger
    template_name = 'example/home.html'


#class StripePaymentView(StripeMixin, BaseMixin, UpdateView):
#
#    model = SalesLedger
#    form_class = ExampleCheckoutForm
#    template_name = 'example_pay/stripe.html'
#
#    def get_success_url(self):
#        return reverse('project.home')


class StripeUpdateView(LoginRequiredMixin, StripeMixin, BaseMixin, UpdateView):

    model = SalesLedger
    form_class = ExampleCheckoutForm
    template_name = 'example/stripe.html'

    def get_success_url(self):
        return reverse('project.home')
