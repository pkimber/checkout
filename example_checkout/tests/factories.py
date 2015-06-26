# -*- encoding: utf-8 -*-
import factory

from example_checkout.models import SalesLedger
from stock.tests.factories import ProductFactory


class SalesLedgerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalesLedger

    product = factory.SubFactory(ProductFactory)
    quantity = 1

    @factory.sequence
    def email(n):
        return '{:02d}@pkimber.net'.format(n)

    @factory.sequence
    def description(n):
        return 'description_{:02d}'.format(n)

    @factory.sequence
    def name(n):
        return 'name_{:02d}'.format(n)
