# -*- encoding: utf-8 -*-
import factory

from datetime import date
from decimal import Decimal

from checkout.models import (
    ContactPaymentPlan,
    ContactPaymentPlanInstalment,
)
from checkout.tests.factories import PaymentPlanFactory
from contact.tests.factories import ContactFactory
from example_checkout.models import SalesLedger
from login.tests.factories import UserFactory
from stock.tests.factories import ProductFactory


class ContactPaymentPlanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ContactPaymentPlan

    contact = factory.SubFactory(ContactFactory)
    content_object = factory.SubFactory(ContactFactory)
    payment_plan = factory.SubFactory(PaymentPlanFactory)
    total = Decimal('100.00')


class ContactPaymentPlanInstalmentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ContactPaymentPlanInstalment

    contact_payment_plan = factory.SubFactory(ContactPaymentPlanFactory)
    deposit = False
    due = date.today()
    amount = Decimal('99.99')

    @factory.sequence
    def count(n):
        return n


class SalesLedgerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalesLedger

    contact = factory.SubFactory(ContactFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
