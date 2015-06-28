# -*- encoding: utf-8 -*-
from django import forms

from .models import (
    Checkout,
    CheckoutAction,
)


CHECKOUT_ACTIONS = (
    (CheckoutAction.PAYMENT, 'Pay Now'),
    (CheckoutAction.PAYMENT_PLAN, 'Payment Plan'),
)


class CheckoutForm(forms.ModelForm):

    action = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHECKOUT_ACTIONS,
    )
    token = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['token'].widget = forms.HiddenInput()
        self.initial['action'] = CheckoutAction.PAYMENT
