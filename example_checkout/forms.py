# -*- encoding: utf-8 -*-
from django import forms

from .models import SalesLedger

from checkout.forms import CheckoutForm


class ExampleCheckoutForm(CheckoutForm):

    class Meta:
        model = SalesLedger
        fields = (
            'checkout_action',
        )
