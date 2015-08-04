# -*- encoding: utf-8 -*-
import pytest
from decimal import Decimal

from django.core.urlresolvers import reverse

from checkout.models import (
    Checkout,
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
def test_post_card_refresh(client, mocker):
    mocker.patch('stripe.Customer.create')
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    data = {
        'action': CheckoutAction.CARD_REFRESH,
    }
    response = client.post(url, data)
    assert 302 == response.status_code
    assert 1 == Checkout.objects.count()
    checkout = Checkout.objects.first()
    assert CheckoutAction.CARD_REFRESH == checkout.action.slug
    assert None == checkout.total


@pytest.mark.django_db
def test_post_invoice(client):
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    data = {
        'action': CheckoutAction.INVOICE,
        'email': 'test@pkimber.net',
    }
    response = client.post(url, data)
    assert 302 == response.status_code
    assert 1 == Checkout.objects.count()
    checkout = Checkout.objects.first()
    assert CheckoutAction.INVOICE == checkout.action.slug
    invoice = checkout.checkoutinvoice
    assert 'test@pkimber.net' == invoice.email
    assert Decimal('0') < checkout.total
