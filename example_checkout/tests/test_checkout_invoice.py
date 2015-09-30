# -*- encoding: utf-8 -*-
import pytest

from checkout.models import CheckoutAction
from checkout.tests.factories import (
    CheckoutFactory,
    CheckoutAdditionalFactory,
)
from example_checkout.tests.factories import SalesLedgerFactory


@pytest.mark.django_db
def test_invoice_data():
    checkout = CheckoutFactory(
        action=CheckoutAction.objects.invoice,
        content_object=SalesLedgerFactory(),
    )
    CheckoutAdditionalFactory(
        checkout=checkout,
        company_name='KB',
        email='test@pkimber.net',
    )
    assert ('KB', 'test@pkimber.net') == tuple(checkout.invoice_data)


@pytest.mark.django_db
def test_invoice_data_none():
    checkout = CheckoutFactory(
        action=CheckoutAction.objects.charge,
        content_object=SalesLedgerFactory(),
    )
    assert () == tuple(checkout.invoice_data)
