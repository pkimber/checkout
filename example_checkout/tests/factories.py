# -*- encoding: utf-8 -*-
import factory

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


class SalesLedgerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalesLedger

    contact = factory.SubFactory(ContactFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
