# -*- encoding: utf-8 -*-
import factory

from datetime import date
from decimal import Decimal

#from checkout.models import (
#    ContactPlan,
#    ContactPlanPayment,
#)
from checkout.tests.factories import PaymentPlanFactory
from contact.tests.factories import ContactFactory
from example_checkout.models import SalesLedger
from login.tests.factories import UserFactory
from stock.tests.factories import ProductFactory


#class ContactPlanFactory(factory.django.DjangoModelFactory):
#
#    class Meta:
#        model = ContactPlan
#
#    contact = factory.SubFactory(ContactFactory)
#    payment_plan = factory.SubFactory(PaymentPlanFactory)
#
#
#class ContactPlanPaymentFactory(factory.django.DjangoModelFactory):
#
#    class Meta:
#        model = ContactPlanPayment
#
#    contact_plan = factory.SubFactory(ContactPlanFactory)
#    due = date.today()
#    amount = Decimal('99.99')
#
#    @factory.sequence
#    def count(n):
#        return n


class SalesLedgerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalesLedger

    contact = factory.SubFactory(ContactFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
