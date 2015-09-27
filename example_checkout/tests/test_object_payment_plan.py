# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from unittest import mock

from django.db import transaction

from checkout.models import (
    CheckoutError,
    CheckoutState,
    ObjectPaymentPlan
)
from checkout.tests.factories import (
    CustomerFactory,
    ObjectPaymentPlanFactory,
    ObjectPaymentPlanInstalmentFactory,
    PaymentPlanFactory,
)
from .factories import ContactFactory


@pytest.mark.django_db
def test_factory():
    ObjectPaymentPlanFactory(content_object=ContactFactory())


@pytest.mark.django_db
def test_str():
    str(ObjectPaymentPlanFactory(content_object=ContactFactory()))


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
    # check deposit - count should be '1' and the 'due' date ``today``
    result = [
        (p.count, p.amount, p.due) for p in object_payment_plan.payments
    ]
    assert [(1, Decimal('20'), date.today())] == result
    # create the instalments
    with transaction.atomic():
        # this must be run within a transaction
        object_payment_plan.create_instalments()
    result = [
        (p.count, p.amount, p.due) for p in object_payment_plan.payments
    ]
    offset = 0
    # instalments start a month later if after the 15th of the month
    if date.today().day > 15:
        offset = 1
    assert [
        (
            1,
            Decimal('20'),
            date.today()
        ),
        (
            2,
            Decimal('40'),
            date.today() + relativedelta(months=+(1+offset), day=1)
        ),
        (
            3,
            Decimal('40'),
            date.today() + relativedelta(months=+(2+offset), day=1)
        ),
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
    obj = ObjectPaymentPlanFactory(content_object=ContactFactory())
    with pytest.raises(CheckoutError) as e:
        obj.create_instalments()
    assert 'no deposit/instalment record' in str(e.value)


@pytest.mark.django_db
def test_create_instalments_corrupt():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=object_payment_plan,
        count=2,
    )
    with pytest.raises(CheckoutError) as e:
        obj.object_payment_plan.create_instalments()
    assert 'no deposit record' in str(e.value)


@pytest.mark.django_db
def test_outstanding_payment_plans():
    assert 0 == ObjectPaymentPlan.objects.outstanding_payment_plans.count()


@pytest.mark.django_db
def test_outstanding_payment_plans_exclude_deleted():
    obj = ObjectPaymentPlanFactory(
        content_object=ContactFactory(),
        deleted=True,
    )
    ObjectPaymentPlanInstalmentFactory(object_payment_plan=obj)
    ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    assert 1 == ObjectPaymentPlan.objects.outstanding_payment_plans.count()


@pytest.mark.django_db
def test_outstanding_payment_plans_exclude_success():
    ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        state=CheckoutState.objects.success,
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    assert 1 == ObjectPaymentPlan.objects.outstanding_payment_plans.count()


@pytest.mark.django_db
def test_outstanding_payment_plans_filter_two():
    obj = ObjectPaymentPlanFactory(content_object=ContactFactory())
    ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=obj
    )
    ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=obj,
        due=date.today() + relativedelta(months=+1),
    )
    assert 1 == ObjectPaymentPlan.objects.outstanding_payment_plans.count()


@pytest.mark.django_db
def test_refresh_card_expiry_dates():
    with mock.patch('stripe.Customer.retrieve') as mock_retrieve:
        mock_retrieve.return_value = {
            'default_card': '1234',
            'cards': {
                'data': [
                    {
                        'id': '1234',
                        'exp_month': '8',
                        'exp_year': '1986',
                    },
                ],
            },
        }
        obj = ObjectPaymentPlanFactory(content_object=ContactFactory())
        ObjectPaymentPlanInstalmentFactory(
            object_payment_plan=obj
        )
        ObjectPaymentPlanInstalmentFactory(
            object_payment_plan=obj,
            due=date.today() + relativedelta(months=+1),
        )
        customer = CustomerFactory(
            email=obj.content_object.checkout_email
        )
        ObjectPaymentPlan.objects.refresh_card_expiry_dates()
        customer.refresh_from_db()
        assert True == customer.refresh


@pytest.mark.django_db
def test_refresh_card_expiry_dates_future():
    with mock.patch('stripe.Customer.retrieve') as mock_retrieve:
        mock_retrieve.return_value = {
            'default_card': '1234',
            'cards': {
                'data': [
                    {
                        'id': '1234',
                        'exp_month': '8',
                        'exp_year': '2050',
                    },
                ],
            },
        }
        obj = ObjectPaymentPlanFactory(content_object=ContactFactory())
        ObjectPaymentPlanInstalmentFactory(
            object_payment_plan=obj
        )
        ObjectPaymentPlanInstalmentFactory(
            object_payment_plan=obj,
            due=date.today() + relativedelta(months=+1),
        )
        customer = CustomerFactory(
            email=obj.content_object.checkout_email
        )
        ObjectPaymentPlan.objects.refresh_card_expiry_dates()
        customer.refresh_from_db()
        assert False == customer.refresh


@pytest.mark.django_db
def test_report_card_expiry_dates():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    ObjectPaymentPlanInstalmentFactory(object_payment_plan=object_payment_plan)
    obj = ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory()
        ),
    )
    CustomerFactory(
        email=obj.object_payment_plan.content_object.checkout_email
    )
    ObjectPaymentPlan.objects.report_card_expiry_dates
