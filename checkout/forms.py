# -*- encoding: utf-8 -*-
from django import forms

from .models import Checkout


#class PayLaterForm(forms.ModelForm):
#
#    class Meta:
#        model = Payment
#        fields = ()


class CheckoutForm(forms.ModelForm):

    stripeToken = forms.CharField()

    class Meta:
        model = Checkout
        fields = ()
