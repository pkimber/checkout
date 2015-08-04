# -*- encoding: utf-8 -*-
import pytest
from decimal import Decimal

from django.core.urlresolvers import reverse

from checkout.models import (
    CheckoutAction,
    CheckoutInvoice,
)
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


@pytest.mark.django_db
def test_post(client):
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    data = {
        'action': CheckoutAction.INVOICE,
        'email': 'test@pkimber.net',
    }
    response = client.post(url, data)
    assert 302 == response.status_code
    invoice = CheckoutInvoice.objects.get(email='test@pkimber.net')
    assert 'invoice' == invoice.checkout.action.slug
