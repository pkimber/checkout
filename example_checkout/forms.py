# -*- encoding: utf-8 -*-
from .models import SalesLedger

from checkout.forms import CheckoutForm


class ExampleCheckoutForm(CheckoutForm):

    class Meta:
        model = SalesLedger
        fields = (
            'action',
        )
