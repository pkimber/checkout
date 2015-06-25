# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import SalesLedger


class ExampleCheckoutForm(forms.ModelForm):

    class Meta:
        model = SalesLedger
        fields = ()
