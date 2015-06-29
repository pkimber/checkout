# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from decimal import Decimal

from checkout.tests.factories import PaymentPlanFactory


@pytest.mark.django_db
def test_factory():
    PaymentPlanFactory()


@pytest.mark.django_db
def test_sample():
    plan = PaymentPlanFactory()
    result = plan.sample(date(2015, 7, 1), Decimal('100'))
    assert [
        (date(2015, 7, 1), Decimal('20')),
        (date(2015, 8, 1), Decimal('40')),
        (date(2015, 9, 1), Decimal('40')),
    ] == result


@pytest.mark.django_db
def test_sample_example():
    plan = PaymentPlanFactory(
        deposit_percent=15,
        count=6,
        interval_in_months=1
    )
    result = plan.sample(date(2015, 7, 6), Decimal('600'))
    print()
    for item in result:
        print(item[0].strftime('%d/%m/%Y'), item[1])
    assert [
        (date(2015, 7, 6), Decimal('90')),
        (date(2015, 8, 6), Decimal('85')),
        (date(2015, 9, 6), Decimal('85')),
        (date(2015, 10, 6), Decimal('85')),
        (date(2015, 11, 6), Decimal('85')),
        (date(2015, 12, 6), Decimal('85')),
        (date(2016, 1, 6), Decimal('85')),
    ] == result
