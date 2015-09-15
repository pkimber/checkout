# -*- encoding: utf-8 -*-
import pytest

from checkout.models import CheckoutError
from checkout.tests.factories import (
    ObjectPaymentPlanFactory,
    PaymentPlanFactory,
)
from .factories import ContactFactory


@pytest.mark.django_db
def test_save():
    obj = PaymentPlanFactory()
    obj.name = 'Another Name'
    obj.save()
    obj.refresh_from_db()
    assert obj.name == 'Another Name'


@pytest.mark.django_db
def test_save_in_use():
    obj = PaymentPlanFactory()
    ObjectPaymentPlanFactory(
        payment_plan=obj,
        content_object=ContactFactory(),
    )
    obj.name = 'Another Name'
    with pytest.raises(CheckoutError) as e:
        obj.save()
    assert 'Payment plan in use.  Cannot be updated.' in str(e.value)


@pytest.mark.django_db
def test_save_not_in_use():
    ObjectPaymentPlanFactory(
        payment_plan=PaymentPlanFactory(),
        content_object=ContactFactory(),
    )
    obj = PaymentPlanFactory()
    obj.name = 'Another Name'
    obj.save()
    obj.refresh_from_db()
    assert obj.name == 'Another Name'
