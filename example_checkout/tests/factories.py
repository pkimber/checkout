# -*- encoding: utf-8 -*-
import factory

from datetime import date
from decimal import Decimal

from checkout.models import (
    ObjectPaymentPlan,
    ObjectPaymentPlanInstalment,
)
from checkout.tests.factories import PaymentPlanFactory
from contact.tests.factories import ContactFactory
from example_checkout.models import SalesLedger
from login.tests.factories import UserFactory
from stock.tests.factories import ProductFactory


class ObjectPaymentPlanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ObjectPaymentPlan

    content_object = factory.SubFactory(ContactFactory)
    payment_plan = factory.SubFactory(PaymentPlanFactory)
    total = Decimal('100.00')


class ObjectPaymentPlanInstalmentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ObjectPaymentPlanInstalment

    object_payment_plan = factory.SubFactory(ObjectPaymentPlanFactory)
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
