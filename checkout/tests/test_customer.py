# -*- encoding: utf-8 -*-
import pytest

from checkout.tests.factories import CustomerFactory


@pytest.mark.django_db
def test_has_customer():
    customer = CustomerFactory()
    assert False == customer.has_customer


@pytest.mark.django_db
def test_has_customer_not():
    customer = CustomerFactory(customer_id='123')
    assert True == customer.has_customer
