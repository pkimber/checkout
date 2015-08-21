# -*- encoding: utf-8 -*-
import pytest

from decimal import Decimal

from django.core.urlresolvers import reverse

from checkout.models import CheckoutAction
from checkout.tests.factories import (
    CheckoutFactory,
    CheckoutSettingsFactory,
)
from example_checkout.tests.factories import SalesLedgerFactory

from checkout.views import CONTENT_OBJECT_PK


def _set_session(client, pk):
    session = client.session
    session[CONTENT_OBJECT_PK] = pk
    session.save()


@pytest.mark.django_db
def test_get(client):
    CheckoutSettingsFactory()
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    obj = CheckoutFactory(
        action=CheckoutAction.objects.payment_plan,
        content_object=obj,
        total=Decimal('20'),
    )
    url = reverse('example.sales.ledger.checkout.success', args=[obj.pk])
    response = client.get(url)
    assert 200 == response.status_code
