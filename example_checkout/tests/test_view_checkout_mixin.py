# -*- encoding: utf-8 -*-
import pytest

from django.core.urlresolvers import reverse

from checkout.views import CONTENT_OBJECT_PK
from example_checkout.tests.factories import SalesLedgerFactory


def _set_session(client, pk):
    session = client.session
    session[CONTENT_OBJECT_PK] = pk
    session.save()


@pytest.mark.django_db
def test_get(client):
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    response = client.get(url)
    assert 200 == response.status_code
