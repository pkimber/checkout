# -*- encoding: utf-8 -*-
from datetime import date

from django import template


register = template.Library()


@register.inclusion_tag('checkout/_payment_plan_example.html')
def checkout_payment_plan_example(payment_plan, total):
    example = payment_plan.example(date.today(), total)
    return dict(example=example, total=total)
