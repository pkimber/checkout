# -*- encoding: utf-8 -*-
import pytest
from decimal import Decimal

from django.core.urlresolvers import reverse

from checkout.models import (
    Checkout,
    CheckoutAction,
)
from checkout.tests.factories import CheckoutSettingsFactory
from checkout.views import CONTENT_OBJECT_PK
from example_checkout.tests.factories import SalesLedgerFactory
from stock.tests.factories import ProductFactory


def _set_session(client, pk):
    session = client.session
    session[CONTENT_OBJECT_PK] = pk
    session.save()


@pytest.mark.django_db
def test_get(client):
    CheckoutSettingsFactory()
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    response = client.get(url)
    assert 200 == response.status_code


@pytest.mark.django_db
def test_post_card_payment(client, mocker):
    mocker.patch('stripe.Charge.create')
    mocker.patch('stripe.Customer.create')
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    data = {
        'action': CheckoutAction.PAYMENT,
        'token': 'my-testing-token',
    }
    response = client.post(url, data)
    assert 302 == response.status_code
    assert 1 == Checkout.objects.count()
    checkout = Checkout.objects.first()
    assert CheckoutAction.PAYMENT == checkout.action.slug
    assert Decimal('0') < checkout.total


@pytest.mark.django_db
def test_post_card_payment_plan(client, mocker):
    mocker.patch('stripe.Customer.create')
    product = ProductFactory(price=Decimal('12.34'))
    obj = SalesLedgerFactory(product=product)
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    data = {
        'action': CheckoutAction.PAYMENT_PLAN,
        'token': 'my-testing-token',
    }
    response = client.post(url, data)
    assert 302 == response.status_code
    assert 1 == Checkout.objects.count()
    checkout = Checkout.objects.first()
    assert CheckoutAction.PAYMENT_PLAN == checkout.action.slug
    assert Decimal('12.34') == checkout.total


@pytest.mark.django_db
def test_post_card_refresh(client, mocker):
    mocker.patch('stripe.Customer.create')
    obj = SalesLedgerFactory()
    _set_session(client, obj.pk)
    url = reverse('example.sales.ledger.checkout', args=[obj.pk])
    data = {
        'action': CheckoutAction.CARD_REFRESH,
        'token': 'my-testing-token',
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
        'company_name': 'KB',
        'address_1': 'My Address',
        'town': 'Hatherleigh',
        'county': 'Devon',
        'postcode': 'EX20',
        'country': 'UK',
        'contact_name': 'Patrick',
        'email': 'test@test.com',
    }
    response = client.post(url, data)
    assert 302 == response.status_code
    assert 1 == Checkout.objects.count()
    checkout = Checkout.objects.first()
    assert CheckoutAction.INVOICE == checkout.action.slug
    invoice = checkout.checkoutinvoice
    assert 'test@test.com' == invoice.email
    assert Decimal('0') < checkout.total
