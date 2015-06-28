# -*- encoding: utf-8 -*-
from django import forms

from .models import (
    Checkout,
    CheckoutAction,
)


CHECKOUT_ACTIONS = {
    CheckoutAction.PAYMENT: 'Pay Now',
    CheckoutAction.PAYMENT_PLAN: 'Payment Plan',
}


class CheckoutForm(forms.ModelForm):

    action = forms.ChoiceField(widget=forms.RadioSelect)
    token = forms.CharField()

    def _action_choices(self, actions):
        result = []
        for item in actions:
            result.append((item, CHECKOUT_ACTIONS[item]))
        return result

    def __init__(self, *args, **kwargs):
        actions = kwargs.pop('actions')
        super().__init__(*args, **kwargs)
        self.fields['action'].choices = self._action_choices(actions)
        self.fields['token'].widget = forms.HiddenInput()
        self.initial['action'] = CheckoutAction.PAYMENT
