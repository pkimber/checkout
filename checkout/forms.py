# -*- encoding: utf-8 -*-
from django import forms

from .models import (
    Checkout,
    CheckoutAction,
)


#class PayLaterForm(forms.ModelForm):
#
#    class Meta:
#        model = Payment
#        fields = ()


#class CheckoutForm(forms.ModelForm):
#
#    stripeToken = forms.CharField()
#
#    class Meta:
#        model = Checkout
#        fields = ()


CHECKOUT_ACTIONS = (
    (CheckoutAction.PAYMENT, 'Pay Now'),
    (CheckoutAction.PAYMENT_PLAN, 'Payment Plan'),
)


class CheckoutForm(forms.ModelForm):

    checkout_action = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHECKOUT_ACTIONS,
    )
    token = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['token'].widget = forms.HiddenInput()
        self.initial['checkout_action'] = CheckoutAction.PAYMENT
