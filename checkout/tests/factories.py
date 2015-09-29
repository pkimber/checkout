# -*- encoding: utf-8 -*-
import factory

from datetime import date
from decimal import Decimal

from django.utils import timezone

from checkout.models import (
    Checkout,
    CheckoutInvoice,
    CheckoutSettings,
    Customer,
    ObjectPaymentPlan,
    ObjectPaymentPlanInstalment,
    PaymentPlan,
)


class CustomerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Customer

    @factory.sequence
    def email(n):
        return '{:02d}@pkimber.net'.format(n)

    @factory.sequence
    def name(n):
        return '{:02d}_name'.format(n)


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

    deposit = 50
    count = 2
    interval = 1

    @factory.sequence
    def name(n):
        return '{:02d}_name'.format(n)

    @factory.sequence
    def slug(n):
        return '{:02d}_slug'.format(n)


class ObjectPaymentPlanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ObjectPaymentPlan

    #content_object = factory.SubFactory(ContactFactory)
    payment_plan = factory.SubFactory(PaymentPlanFactory)
    total = Decimal('100.00')


class ObjectPaymentPlanInstalmentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ObjectPaymentPlanInstalment

    #object_payment_plan = factory.SubFactory(ObjectPaymentPlanFactory)
    deposit = False
    due = date.today()
    amount = Decimal('99.99')

    @factory.sequence
    def count(n):
        return n


class CheckoutSettingsFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CheckoutSettings

    default_payment_plan = factory.SubFactory(PaymentPlanFactory)
