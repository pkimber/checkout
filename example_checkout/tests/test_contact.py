# -*- encoding: utf-8 -*-
import pytest

from checkout.tests.helper import check_object_payment_plan
from example_checkout.tests.factories import ContactFactory


@pytest.mark.django_db
def test_check_checkout():
    obj = ContactFactory()
    check_object_payment_plan(obj)
