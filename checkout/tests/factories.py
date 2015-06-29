# -*- encoding: utf-8 -*-
import factory

from checkout.models import (
    Checkout,
    Customer,
    PaymentPlan,
)


class CustomerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Customer

    @factory.sequence
    def email(n):
        return '{:02d}@pkimber.net'.format(n)


class CheckoutFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Checkout

    customer = factory.SubFactory(CustomerFactory)


class PaymentPlanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = PaymentPlan

    deposit = 20
    count = 2
    interval = 1
