# -*- encoding: utf-8 -*-
from django import forms

from .models import (
    CheckoutAction,
    PaymentPlan,
)


class CheckoutForm(forms.ModelForm):

    action = forms.ChoiceField(widget=forms.RadioSelect)
    token = forms.CharField()

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
        self.fields['token'].widget = forms.HiddenInput()


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
