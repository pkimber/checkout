# -*- encoding: utf-8 -*-
import pytest

from checkout.tests.helper import check_checkout
from example_checkout.tests.factories import SalesLedgerFactory
from finance.tests.factories import VatSettingsFactory


@pytest.mark.django_db
def test_link_to_payment():
    VatSettingsFactory()
    sales_ledger = SalesLedgerFactory()
    check_checkout(sales_ledger)
