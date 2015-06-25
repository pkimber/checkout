# -*- encoding: utf-8 -*-
from django import forms

from .models import SalesLedger

CHECKOUT_CHOICES = (
    ('1', 'Pay Now'),
    ('2', 'Refresh Card'),
)

class ExampleCheckoutForm(forms.ModelForm):

    choices = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHECKOUT_CHOICES,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['choices'] = '1'

    class Meta:
        model = SalesLedger
        fields = ()
