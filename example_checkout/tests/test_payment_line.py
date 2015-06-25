# -*- encoding: utf-8 -*-
import pytest

from example_checkout.tests.factories import SalesLedgerFactory
from finance.tests.factories import VatSettingsFactory


#@pytest.mark.django_db
#def test_payment_line_str():
#    VatSettingsFactory()
#    sales_ledger = SalesLedgerFactory()
#    payment = sales_ledger.create_payment()
#    payment_line = payment.paymentline_set.first()
#    str(payment_line)
