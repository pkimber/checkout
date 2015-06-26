# -*- encoding: utf-8 -*-
import factory

from checkout.models import (
    Checkout,
    Customer,
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
