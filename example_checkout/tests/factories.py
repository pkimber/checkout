# -*- encoding: utf-8 -*-
import factory

from datetime import date
from decimal import Decimal

from checkout.models import (
    ContactPlan,
    ContactPlanPayment,
)
from checkout.tests.factories import PaymentPlanFactory
from example_checkout.models import (
    Contact,
    SalesLedger,
)
from login.tests.factories import UserFactory
from stock.tests.factories import ProductFactory


class ContactFactory(factory.django.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Contact


class ContactPlanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ContactPlan

    contact = factory.SubFactory(ContactFactory)
    payment_plan = factory.SubFactory(PaymentPlanFactory)


class ContactPlanPaymentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ContactPlanPayment

    contact_plan = factory.SubFactory(ContactPlanFactory)
    due = date.today()
    amount = Decimal('99.99')


class SalesLedgerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalesLedger

    contact = factory.SubFactory(ContactFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
