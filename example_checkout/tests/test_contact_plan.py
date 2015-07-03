# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from decimal import Decimal

from django.db import transaction

from checkout.models import ContactPlan
from checkout.tests.factories import PaymentPlanFactory
from .factories import (
    ContactFactory,
    ContactPlanFactory,
    ContactPlanPaymentFactory,
)


@pytest.mark.django_db
def test_factory_contact_plan():
    ContactPlanFactory()


@pytest.mark.django_db
def test_factory_contact_plan_payment():
    ContactPlanPaymentFactory()


@pytest.mark.django_db
def test_factory_contact_plan_payment_str():
    str(ContactPlanPaymentFactory())


@pytest.mark.django_db
def test_factory_contact_plan_str():
    str(ContactPlanFactory())


@pytest.mark.django_db
def test_create_contact_plan():
    contact = ContactFactory()
    payment_plan = PaymentPlanFactory(
        deposit=20,
        count=2,
        interval=1,
    )
    with transaction.atomic():
        # this must be run within a transaction
        ContactPlan.objects.create_contact_plan(
            contact,
            payment_plan,
            date(2015, 7, 1),
            Decimal('100')
        )
    contact_plan = ContactPlan.objects.get(contact=contact)
    result = [(p.due, p.amount) for p in contact_plan.payments]
    assert [
        (date(2015, 7, 1), Decimal('20')),
        (date(2015, 8, 1), Decimal('40')),
        (date(2015, 9, 1), Decimal('40')),
    ] == result
