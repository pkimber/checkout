# -*- encoding: utf-8 -*-
import pytest

from datetime import date

from checkout.tests.factories import CustomerFactory


@pytest.mark.django_db
def test_customer_refresh():
    customer = CustomerFactory(refresh=True)
    assert True == customer.refresh


@pytest.mark.django_db
def test_customer_refresh_default():
    customer = CustomerFactory()
    assert False == customer.refresh


@pytest.mark.django_db
def test_is_expiring_future():
    customer = CustomerFactory(expiry_date=date(3000, 2, 1))
    assert False == customer.is_expiring


@pytest.mark.django_db
def test_is_expiring_none():
    customer = CustomerFactory()
    assert False == customer.is_expiring


@pytest.mark.django_db
def test_is_expiring_past():
    customer = CustomerFactory(expiry_date=date(2015, 2, 1))
    assert True == customer.is_expiring
