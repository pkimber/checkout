# -*- encoding: utf-8 -*-
import factory

from django.utils import timezone

from checkout.models import (
    Checkout,
    CheckoutInvoice,
    CheckoutSettings,
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
    checkout_date = timezone.now()


class CheckoutInvoiceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CheckoutInvoice

    checkout = factory.SubFactory(CheckoutFactory)


class PaymentPlanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = PaymentPlan

    deposit = 20
    count = 2
    interval = 1

    @factory.sequence
    def name(n):
        return '{:02d}_name'.format(n)

    @factory.sequence
    def slug(n):
        return '{:02d}_slug'.format(n)


class CheckoutSettingsFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CheckoutSettings

    default_payment_plan = factory.SubFactory(PaymentPlanFactory)
