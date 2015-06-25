# -*- encoding: utf-8 -*-
from django import forms

from .models import Checkout


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


CHECKOUT_CHOICES = (
    ('1', 'Pay Now'),
    ('2', 'Refresh Card'),
)


class CheckoutForm(forms.ModelForm):

    checkout_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHECKOUT_CHOICES,
    )
    token = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['token'].widget = forms.HiddenInput()
        self.initial['checkout_type'] = '1'
