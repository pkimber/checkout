# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import transaction

from checkout.models import (
    CheckoutError,
    CheckoutState,
    ObjectPaymentPlan
)
from checkout.tests.factories import PaymentPlanFactory
from .factories import (
    ContactFactory,
    ObjectPaymentPlanFactory,
    ObjectPaymentPlanInstalmentFactory,
)


@pytest.mark.django_db
def test_factory():
    ObjectPaymentPlanFactory()


@pytest.mark.django_db
def test_str():
    str(ObjectPaymentPlanFactory())


@pytest.mark.django_db
def test_create_object_payment_plan():
    contact = ContactFactory()
    payment_plan = PaymentPlanFactory(
        deposit=20,
        count=2,
        interval=1,
    )
    # create the contact plan with the deposit
    with transaction.atomic():
        # this must be run within a transaction
        ObjectPaymentPlan.objects.create_object_payment_plan(
            contact,
            payment_plan,
            Decimal('100')
        )
    object_payment_plan = ObjectPaymentPlan.objects.for_content_object(contact)
    # check deposit - count should be '1' and the 'due' date should be 'None'
    result = [
        (p.count, p.amount, p.due) for p in object_payment_plan.payments
    ]
    assert [(1, Decimal('20'), None)] == result
    # create the instalments
    with transaction.atomic():
        # this must be run within a transaction
        object_payment_plan.create_instalments()
    result = [
        (p.count, p.amount, p.due) for p in object_payment_plan.payments
    ]
    assert [
        (1, Decimal('20'), None),
        (2, Decimal('40'), date.today() + relativedelta(months=+1)),
        (3, Decimal('40'), date.today() + relativedelta(months=+2)),
    ] == result


@pytest.mark.django_db
def test_create_instalments_once_only():
    contact = ContactFactory()
    payment_plan = PaymentPlanFactory(deposit=20, count=2, interval=1)
    # create the contact plan with the deposit
    with transaction.atomic():
        # this must be run within a transaction
        contact_pp = ObjectPaymentPlan.objects.create_object_payment_plan(
            contact,
            payment_plan,
            Decimal('100')
        )
    # create the instalments
    with transaction.atomic():
        # this must be run within a transaction
        contact_pp.create_instalments()
    with pytest.raises(CheckoutError) as e:
        contact_pp.create_instalments()
    assert 'instalments already created' in str(e.value)


@pytest.mark.django_db
def test_create_instalments_no_deposit():
    obj = ObjectPaymentPlanFactory()
    with pytest.raises(CheckoutError) as e:
        obj.create_instalments()
    assert 'no deposit/instalment record' in str(e.value)


@pytest.mark.django_db
def test_create_instalments_corrupt():
    obj = ObjectPaymentPlanInstalmentFactory(count=2)
    with pytest.raises(CheckoutError) as e:
        obj.object_payment_plan.create_instalments()
    assert 'no deposit record' in str(e.value)


@pytest.mark.django_db
def test_outstanding_payment_plans():
    assert 0 == ObjectPaymentPlan.objects.outstanding_payment_plans.count()


@pytest.mark.django_db
def test_outstanding_payment_plans_exclude_deleted():
    ObjectPaymentPlanInstalmentFactory()
    ObjectPaymentPlanInstalmentFactory(state=CheckoutState.objects.success)
    assert 1 == ObjectPaymentPlan.objects.outstanding_payment_plans.count()


@pytest.mark.django_db
def test_outstanding_payment_plans_exclude_success():
    ObjectPaymentPlanInstalmentFactory()
    ObjectPaymentPlanInstalmentFactory(state=CheckoutState.objects.success)
    assert 1 == ObjectPaymentPlan.objects.outstanding_payment_plans.count()
