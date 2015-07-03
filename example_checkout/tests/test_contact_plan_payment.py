# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import transaction

from checkout.models import (
    CheckoutState,
    ContactPlan,
    ContactPlanPayment,
)
from checkout.tests.factories import PaymentPlanFactory
from checkout.tests.helper import check_checkout
from login.tests.factories import UserFactory
from .factories import (
    ContactFactory,
    ContactPlanFactory,
    ContactPlanPaymentFactory,
)


@pytest.mark.django_db
def test_check_checkout():
    obj = ContactPlanPaymentFactory()
    check_checkout(obj)


@pytest.mark.django_db
def test_checkout_description():
    payment_plan = PaymentPlanFactory(
        name='pkimber',
        deposit=50,
        count=2,
        interval=1
    )
    contact_plan = ContactPlan.objects.create_contact_plan(
        ContactFactory(),
        payment_plan,
        date.today(),
        Decimal('100')
    )
    obj = ContactPlanPayment.objects.get(count=2)
    assert ['pkimber', 'Instalment 2 of 3'] == obj.checkout_description


@pytest.mark.django_db
def test_checkout_fail():
    obj = ContactPlanPaymentFactory()
    assert CheckoutState.objects.pending == obj.state
    obj.checkout_fail
    assert CheckoutState.objects.fail == obj.state


@pytest.mark.django_db
def test_checkout_name():
    payment_plan = PaymentPlanFactory(
        name='pkimber',
        deposit=50,
        count=2,
        interval=1
    )
    user = UserFactory(first_name='Patrick', last_name='Kimber')
    contact_plan = ContactPlan.objects.create_contact_plan(
        ContactFactory(user=user),
        payment_plan,
        date.today(),
        Decimal('100'),
    )
    obj = ContactPlanPayment.objects.get(count=2)
    assert 'Patrick Kimber' == obj.checkout_name


@pytest.mark.django_db
def test_checkout_success():
    obj = ContactPlanPaymentFactory()
    assert CheckoutState.objects.pending == obj.state
    obj.checkout_success
    assert CheckoutState.objects.success == obj.state


@pytest.mark.django_db
def test_checkout_total():
    payment_plan = PaymentPlanFactory(
        name='pkimber',
        deposit=50,
        count=2,
        interval=1
    )
    user = UserFactory(first_name='Patrick', last_name='Kimber')
    contact_plan = ContactPlan.objects.create_contact_plan(
        ContactFactory(user=user),
        payment_plan,
        date.today(),
        Decimal('100'),
    )
    assert Decimal('50') == ContactPlanPayment.objects.get(count=1).checkout_total
    assert Decimal('25') == ContactPlanPayment.objects.get(count=2).checkout_total
    assert Decimal('25') == ContactPlanPayment.objects.get(count=3).checkout_total


@pytest.mark.django_db
def test_checkout_email():
    user = UserFactory(email='me@test.com')
    contact = ContactFactory(user=user)
    contact_plan = ContactPlanFactory(contact=contact)
    obj = ContactPlanPaymentFactory(contact_plan=contact_plan)
    assert 'me@test.com' == obj.checkout_email


@pytest.mark.django_db
def test_due():
    today = date.today()
    ContactPlanPaymentFactory(
        count=1,
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPlanPaymentFactory(
        count=2,
        due=today+relativedelta(days=2),
        amount=Decimal('2')
    )
    result = [(p.count, p.amount) for p in ContactPlanPayment.objects.due]
    assert [
        (1, Decimal('1')),
        (2, Decimal('2')),
    ] == result


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
def test_process_payments():
    today = date.today()
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPlanPaymentFactory(
        due=today+relativedelta(days=2),
        amount=Decimal('2')
    )
    ContactPlanPayment.objects.process_payments


@pytest.mark.django_db
def test_str():
    str(ContactPlanPaymentFactory())
