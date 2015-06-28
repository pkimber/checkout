# -*- encoding: utf-8 -*-
from django import forms

from checkout.forms import CheckoutForm
from .models import SalesLedger


class SalesLedgerCheckoutForm(CheckoutForm):

    class Meta:
        model = SalesLedger
        fields = (
            'action',
        )


class SalesLedgerEmptyForm(forms.ModelForm):

    class Meta:
        model = SalesLedger
        fields = ()
