# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import transaction

from checkout.models import ContactPaymentPlan
from checkout.tests.factories import PaymentPlanFactory
from .factories import (
    ContactFactory,
    #ContactPlanFactory,
    #ContactPlanPaymentFactory,
)


#@pytest.mark.django_db
#def test_factory():
#    ContactPlanFactory()
#
#
#@pytest.mark.django_db
#def test_str():
#    str(ContactPlanFactory())


@pytest.mark.django_db
def test_create_contact_plan():
    contact = ContactFactory()
    payment_plan = PaymentPlanFactory(
        deposit=20,
        count=2,
        interval=1,
    )
    # create the contact plan with the deposit
    with transaction.atomic():
        # this must be run within a transaction
        ContactPaymentPlan.objects.create_contact_payment_plan(
            contact,
            contact,
            payment_plan,
            Decimal('100')
        )
    contact_payment_plan = ContactPaymentPlan.objects.get(contact=contact)
    # check deposit - count should be '1' and the 'due' date should be 'None'
    result = [
        (p.count, p.amount, p.due) for p in contact_payment_plan.payments
    ]
    assert [(1, Decimal('20'), None)] == result
    # create the instalments
    with transaction.atomic():
        # this must be run within a transaction
        contact_payment_plan.create_instalments()
    result = [
        (p.count, p.amount, p.due) for p in contact_payment_plan.payments
    ]
    assert [
        (1, Decimal('20'), None),
        (2, Decimal('40'), date.today() + relativedelta(months=+1)),
        (3, Decimal('40'), date.today() + relativedelta(months=+2)),
    ] == result
