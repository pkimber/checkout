# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from checkout.models import (
    CheckoutState,
    ContactPlanPayment,
)
from .factories import (
    ContactPlanFactory,
    ContactPlanPaymentFactory,
)


@pytest.mark.django_db
def test_due():
    today = date.today()
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=2),
        amount=Decimal('2')
    )
    result = [p.amount for p in ContactPlanPayment.objects.due]
    assert [Decimal('1'), Decimal('2')] == result


@pytest.mark.django_db
def test_due_plan_deleted():
    today = date.today()
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    contact_plan = ContactPlanFactory(deleted=True)
    ContactPlanPaymentFactory(
        contact_plan=contact_plan,
        due=today+relativedelta(days=2),
        amount=Decimal('2')
    )
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=3),
        amount=Decimal('3')
    )
    result = [p.amount for p in ContactPlanPayment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_due_not_due():
    today = date.today()
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=-1),
        amount=Decimal('2')
    )
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=3),
        amount=Decimal('3')
    )
    result = [p.amount for p in ContactPlanPayment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_due_not_pending():
    today = date.today()
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=2),
        state=CheckoutState.objects.fail,
        amount=Decimal('2')
    )
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=3),
        amount=Decimal('3')
    )
    result = [p.amount for p in ContactPlanPayment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_factory():
    ContactPlanPaymentFactory()


@pytest.mark.django_db
def test_str():
    str(ContactPlanPaymentFactory())
