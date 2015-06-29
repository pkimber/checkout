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
    print()
    for item in result:
        print(item)
    assert [
        (date(2015, 7, 1), Decimal('20')),
        (date(2015, 8, 1), Decimal('40')),
        (date(2015, 9, 1), Decimal('40')),
    ] == result
