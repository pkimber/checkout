# -*- encoding: utf-8 -*-
from django import forms

from .models import (
    CheckoutAction,
    ObjectPaymentPlanInstalment,
    PaymentPlan,
)


class CheckoutForm(forms.ModelForm):

    action = forms.ChoiceField(widget=forms.RadioSelect)

    company_name = forms.CharField(required=False)
    address_1 = forms.CharField(label='Address', required=False)
    address_2 = forms.CharField(label='', required=False)
    address_3 = forms.CharField(label='', required=False)
    town = forms.CharField(required=False)
    county = forms.CharField(required=False)
    postcode = forms.CharField(required=False)
    country = forms.CharField(required=False)
    # contact
    contact_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)

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
                'company_name',
                'address_1',
                'address_2',
                'address_3',
                'town',
                'county',
                'postcode',
                'country',
                'contact_name',
                'email',
                'phone',
                ):
                self.fields[name].widget = forms.HiddenInput()
        # hide token field
        self.fields['token'].widget = forms.HiddenInput()

    def invoice_data(self):
        return dict(
            company_name=self.cleaned_data['company_name'],
            address_1=self.cleaned_data['address_1'],
            address_2=self.cleaned_data['address_2'],
            address_3=self.cleaned_data['address_3'],
            town=self.cleaned_data['town'],
            county=self.cleaned_data['county'],
            postcode=self.cleaned_data['postcode'],
            country=self.cleaned_data['country'],
            contact_name=self.cleaned_data['contact_name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
        )


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
