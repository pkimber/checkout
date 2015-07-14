# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.core.exceptions import ValidationError

from checkout.tests.factories import PaymentPlanFactory


@pytest.mark.django_db
def test_factory():
    PaymentPlanFactory()


@pytest.mark.django_db
def test_count_greater_zero():
    obj = PaymentPlanFactory(deposit=10, count=0, interval=1)
    with pytest.raises(ValidationError):
        obj.full_clean()


@pytest.mark.django_db
def test_deposit_greater_zero():
    obj = PaymentPlanFactory(deposit=0, count=6, interval=1)
    with pytest.raises(ValidationError):
        obj.full_clean()


@pytest.mark.django_db
def test_interval_greater_zero():
    obj = PaymentPlanFactory(deposit=10, count=6, interval=0)
    with pytest.raises(ValidationError):
        obj.full_clean()


@pytest.mark.django_db
def test_simple():
    plan = PaymentPlanFactory(
        deposit=20,
        count=2,
        interval=1
    )
    total = Decimal('100')
    # deposit
    assert Decimal('20') == plan.deposit_amount(total)
    # instalments
    result = plan.instalments(total)
    assert [
        (date.today() + relativedelta(months=+1), Decimal('40')),
        (date.today() + relativedelta(months=+2), Decimal('40')),
    ] == result


@pytest.mark.django_db
def test_illustration_typical():
    plan = PaymentPlanFactory(
        deposit=15,
        count=6,
        interval=1
    )
    total = Decimal('600')
    # deposit
    assert Decimal('90') == plan.deposit_amount(total)
    # instalments
    result = plan.instalments(total)
    assert [
        (date.today() + relativedelta(months=+1), Decimal('85')),
        (date.today() + relativedelta(months=+2), Decimal('85')),
        (date.today() + relativedelta(months=+3), Decimal('85')),
        (date.today() + relativedelta(months=+4), Decimal('85')),
        (date.today() + relativedelta(months=+5), Decimal('85')),
        (date.today() + relativedelta(months=+6), Decimal('85')),
    ] == result


@pytest.mark.django_db
def test_illustration_awkward():
    plan = PaymentPlanFactory(
        deposit=50,
        count=3,
        interval=2
    )
    total = Decimal('200')
    # deposit
    assert Decimal('100') == plan.deposit_amount(total)
    # instalments
    result = plan.instalments(total)
    assert [
        (date.today() + relativedelta(months=+2), Decimal('33.33')),
        (date.today() + relativedelta(months=+4), Decimal('33.33')),
        (date.today() + relativedelta(months=+6), Decimal('33.34')),
    ] == result


#@pytest.mark.django_db
#def test_example():
#    plan = PaymentPlanFactory(
#        deposit=50,
#        count=2,
#        interval=1
#    )
#    result = [item[1] for item in plan.example]
#    assert [Decimal('50'), Decimal('25'), Decimal('25')] == result
