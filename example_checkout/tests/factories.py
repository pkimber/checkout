# -*- encoding: utf-8 -*-
import factory

from datetime import date
from decimal import Decimal

from contact.tests.factories import ContactFactory
from example_checkout.models import SalesLedger
from stock.tests.factories import ProductFactory


class SalesLedgerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalesLedger

    contact = factory.SubFactory(ContactFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
