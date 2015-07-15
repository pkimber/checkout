# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import transaction

from checkout.models import (
    CheckoutState,
    ContactPaymentPlan,
    ContactPaymentPlanInstalment,
)
from checkout.tests.factories import PaymentPlanFactory
from checkout.tests.helper import check_checkout
from login.tests.factories import UserFactory
from .factories import (
    ContactFactory,
    ContactPaymentPlanFactory,
    ContactPaymentPlanInstalmentFactory,
)


@pytest.mark.django_db
def test_check_checkout():
    with transaction.atomic():
        # this must be run within a transaction
        obj = ContactPaymentPlan.objects.create_contact_payment_plan(
            ContactFactory(),
            ContactFactory(),
            PaymentPlanFactory(),
            Decimal('100')
        )
    instalment = ContactPaymentPlanInstalment.objects.get(
        contact_payment_plan=obj
    )
    check_checkout(instalment)


@pytest.mark.django_db
def test_checkout_description():
    payment_plan = PaymentPlanFactory(
        name='pkimber',
        deposit=50,
        count=2,
        interval=1
    )
    # create the plan and the deposit
    contact_pp = ContactPaymentPlan.objects.create_contact_payment_plan(
        ContactFactory(),
        ContactFactory(),
        payment_plan,
        Decimal('100'),
    )
    # create the instalments
    contact_pp.create_instalments()
    # check
    instalments = ContactPaymentPlanInstalment.objects.filter(
        contact_payment_plan=contact_pp
    )
    assert 3 == instalments.count()
    assert [
        'pkimber', 'Instalment 2 of 3'
    ] == instalments[1].checkout_description


@pytest.mark.django_db
def test_checkout_fail():
    with transaction.atomic():
        # this must be run within a transaction
        obj = ContactPaymentPlan.objects.create_contact_payment_plan(
            ContactFactory(),
            ContactFactory(),
            PaymentPlanFactory(),
            Decimal('100')
        )
    obj = ContactPaymentPlanInstalment.objects.get(
        contact_payment_plan=obj
    )
    assert CheckoutState.objects.pending == obj.state
    obj.checkout_fail
    assert CheckoutState.objects.fail == obj.state


@pytest.mark.django_db
def test_checkout_name():
    user = UserFactory(first_name='Patrick', last_name='Kimber')
    contact_pp = ContactPaymentPlan.objects.create_contact_payment_plan(
        ContactFactory(user=user),
        ContactFactory(),
        PaymentPlanFactory(),
        Decimal('100'),
    )
    obj = ContactPaymentPlanInstalment.objects.get(
        contact_payment_plan=contact_pp
    )
    assert 'Patrick Kimber' == obj.checkout_name


@pytest.mark.django_db
def test_checkout_success():
    contact_pp = ContactPaymentPlan.objects.create_contact_payment_plan(
        ContactFactory(),
        ContactFactory(),
        PaymentPlanFactory(),
        Decimal('100'),
    )
    obj = ContactPaymentPlanInstalment.objects.get(
        contact_payment_plan=contact_pp
    )
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
    contact_pp = ContactPaymentPlan.objects.create_contact_payment_plan(
        ContactFactory(user=user),
        ContactFactory(),
        payment_plan,
        Decimal('100'),
    )
    contact_pp.create_instalments()
    assert Decimal('50') == ContactPaymentPlanInstalment.objects.get(
        count=1
    ).checkout_total
    assert Decimal('25') == ContactPaymentPlanInstalment.objects.get(
        count=2
    ).checkout_total
    assert Decimal('25') == ContactPaymentPlanInstalment.objects.get(
        count=3
    ).checkout_total


@pytest.mark.django_db
def test_checkout_email():
    user = UserFactory(email='me@test.com')
    contact_pp = ContactPaymentPlan.objects.create_contact_payment_plan(
        ContactFactory(user=user),
        ContactFactory(),
        PaymentPlanFactory(),
        Decimal('100'),
    )
    obj = ContactPaymentPlanInstalment.objects.get(
        contact_payment_plan=contact_pp
    )
    assert 'me@test.com' == obj.checkout_email


@pytest.mark.django_db
def test_due():
    today = date.today()
    ContactPaymentPlanInstalmentFactory(
        count=1,
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPaymentPlanInstalmentFactory(
        count=2,
        due=today+relativedelta(days=2),
        amount=Decimal('2')
    )
    result = [p.amount for p in ContactPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('2')] == result


@pytest.mark.django_db
def test_due_plan_deleted():
    today = date.today()
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    contact_payment_plan = ContactPaymentPlanFactory(deleted=True)
    ContactPaymentPlanInstalmentFactory(
        contact_payment_plan=contact_payment_plan,
        due=today+relativedelta(days=2),
        amount=Decimal('2')
    )
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=3),
        amount=Decimal('3')
    )
    result = [p.amount for p in ContactPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_due_not_due():
    today = date.today()
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-1),
        amount=Decimal('2')
    )
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=3),
        amount=Decimal('3')
    )
    result = [p.amount for p in ContactPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_due_not_pending():
    today = date.today()
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=2),
        state=CheckoutState.objects.fail,
        amount=Decimal('2')
    )
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=3),
        amount=Decimal('3')
    )
    result = [p.amount for p in ContactPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_factory():
    ContactPaymentPlanInstalmentFactory()


@pytest.mark.django_db
def test_process_payments():
    """Process payments.

    I cannot get this to run as a test because I don't know how to create a
    test Stripe customer.

    """
    today = date.today()
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('1')
    )
    ContactPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=2),
        amount=Decimal('2')
    )
    # TODO Uncomment this if I can work out how to create a test Stripe customer
    # ContactPlanPayment.objects.process_payments


@pytest.mark.django_db
def test_str():
    str(ContactPaymentPlanFactory())
