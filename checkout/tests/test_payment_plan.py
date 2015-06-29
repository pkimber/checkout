# -*- encoding: utf-8 -*-
import pytest

from datetime import date
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
def test_illustration():
    plan = PaymentPlanFactory()
    result = plan.illustration(date(2015, 7, 1), Decimal('100'))
    assert [
        (date(2015, 7, 1), Decimal('20')),
        (date(2015, 8, 1), Decimal('40')),
        (date(2015, 9, 1), Decimal('40')),
    ] == result


@pytest.mark.django_db
def test_illustration_example():
    plan = PaymentPlanFactory(
        deposit=15,
        count=6,
        interval=1
    )
    result = plan.illustration(date(2015, 7, 6), Decimal('600'))
    assert [
        (date(2015, 7, 6), Decimal('90')),
        (date(2015, 8, 6), Decimal('85')),
        (date(2015, 9, 6), Decimal('85')),
        (date(2015, 10, 6), Decimal('85')),
        (date(2015, 11, 6), Decimal('85')),
        (date(2015, 12, 6), Decimal('85')),
        (date(2016, 1, 6), Decimal('85')),
    ] == result


@pytest.mark.django_db
def test_illustration_awkward():
    plan = PaymentPlanFactory(
        deposit=50,
        count=3,
        interval=1
    )
    result = plan.illustration(date(2015, 7, 1), Decimal('200'))
    assert [
        (date(2015, 7, 1), Decimal('100')),
        (date(2015, 8, 1), Decimal('33.33')),
        (date(2015, 9, 1), Decimal('33.33')),
        (date(2015, 10, 1), Decimal('33.34')),
    ] == result


@pytest.mark.django_db
def test_sample():
    plan = PaymentPlanFactory(
        deposit=50,
        count=3,
        interval=1
    )
    assert (
        'For a total of £600, we pay an initial deposit of £300.00 followed '
        'by 2 payments of £100.00 and a final payment of £100.00'
    ) == plan.sample
