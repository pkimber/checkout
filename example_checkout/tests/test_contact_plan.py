# -*- encoding: utf-8 -*-
import pytest

from .factories import (
    ContactPlanFactory,
    ContactPlanPaymentFactory,
)


@pytest.mark.django_db
def test_factory_contact_plan():
    ContactPlanFactory()


@pytest.mark.django_db
def test_factory_contact_plan_payment():
    ContactPlanPaymentFactory()


@pytest.mark.django_db
def test_factory_contact_plan_payment_str():
    str(ContactPlanPaymentFactory())


@pytest.mark.django_db
def test_factory_contact_plan_str():
    str(ContactPlanFactory())
