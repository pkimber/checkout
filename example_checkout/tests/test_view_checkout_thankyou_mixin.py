# -*- encoding: utf-8 -*-
import pytest

from django.core.urlresolvers import reverse

from checkout.models import CheckoutAction
from checkout.tests.factories import CheckoutFactory
from example_checkout.tests.factories import SalesLedgerFactory


@pytest.mark.django_db
def test_get(client):
    obj = CheckoutFactory(
        action=CheckoutAction.objects.payment,
        content_object=SalesLedgerFactory(),
    )
    url = reverse('example.sales.ledger.checkout.thankyou', args=[obj.pk])
    response = client.get(url)
    assert 200 == response.status_code
