# -*- encoding: utf-8 -*-
from django import forms

from .models import (
    CheckoutAction,
    ObjectPaymentPlanInstalment,
    PaymentPlan,
)


class CheckoutForm(forms.ModelForm):

    action = forms.ChoiceField(widget=forms.RadioSelect)

    contact_name = forms.CharField(required=False)
    invoice_email = forms.EmailField(required=False)
    company_name = forms.CharField(max_length=100)
    address_1 = forms.CharField(label='Address', required=True)
    address_2 = forms.CharField(label='', required=True)
    address_3 = forms.CharField(label='', required=True)
    town = forms.CharField(max_length=100, required=True)
    county = forms.CharField(max_length=100, required=True)
    postcode = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=100, required=True)

    # token is not required for payment by invoice
    token = forms.CharField(required=False)

    def _action_choices(self, actions):
        result = []
        for item in actions:
            obj = CheckoutAction.objects.get(slug=item)
            result.append((item, obj.name))
        return result

    def __init__(self, *args, **kwargs):
        actions = kwargs.pop('actions')
        super().__init__(*args, **kwargs)
        choices = self._action_choices(actions)
        self.fields['action'].choices = choices
        if len(choices) == 1:
            self.fields['action'].widget = forms.HiddenInput()
            self.initial['action'] = choices[0][0]
        elif CheckoutAction.PAYMENT in actions:
            self.initial['action'] = CheckoutAction.PAYMENT
        # hide invoice fields if not used
        if not CheckoutAction.INVOICE in actions:
            for name in (
                'invoice_email',
                'company_name',
                'address_1',
                'address_2',
                ):
                self.fields[name].widget = forms.HiddenInput()
        # hide token field
        self.fields['token'].widget = forms.HiddenInput()


class ObjectPaymentPlanInstalmentEmptyForm(forms.ModelForm):

    class Meta:
        model = ObjectPaymentPlanInstalment
        fields = ()


class PaymentPlanEmptyForm(forms.ModelForm):

    class Meta:
        model = PaymentPlan
        fields = ()


class PaymentPlanForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'pure-input-1-2', 'rows': 4}
        )

    class Meta:
        model = PaymentPlan
        fields = (
            'slug',
            'name',
            'deposit',
            'count',
            'interval',
        )
