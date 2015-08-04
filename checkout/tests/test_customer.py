# -*- encoding: utf-8 -*-
import pytest

from checkout.tests.factories import CustomerFactory


@pytest.mark.django_db
def test_customer_refresh():
    customer = CustomerFactory(refresh=True)
    assert True == customer.refresh


@pytest.mark.django_db
def test_customer_refresh_default():
    customer = CustomerFactory()
    assert False == customer.refresh
