# -*- encoding: utf-8 -*-
from decimal import Decimal

import factory

from finance.models import VatSettings
from checkout.models import (
    Checkout,
    Customer,
    #PaymentLine,
)
from stock.tests.factories import ProductFactory


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


#class PaymentLineFactory(factory.django.DjangoModelFactory):
#    """Create a payment line.
#
#    To customise::
#
#      payment = PaymentFactory(content_object=SalesLedgerFactory())
#      product = ProductFactory(name='Paintbrush')
#      PaymentLineFactory(payment=payment, product=product)
#
#    """
#
#    class Meta:
#        model = PaymentLine
#
#    payment = factory.SubFactory(PaymentFactory)
#    product = factory.SubFactory(ProductFactory)
#    quantity = Decimal('1')
#
#    @factory.lazy_attribute
#    def vat_code(self):
#        return VatSettings.objects.settings().standard_vat_code
#
#    @factory.sequence
#    def line_number(n):
#        return n
