# -*- encoding: utf-8 -*-
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.test import TestCase

from checkout.views import CHECKOUT_PK
from example_checkout.tests.factories import SalesLedgerFactory
from finance.tests.factories import VatSettingsFactory
from login.tests.factories import TEST_PASSWORD
from login.tests.scenario import (
    default_scenario_login,
    get_user_web,
)
from mail.models import Notify
from stock.models import (
    Product,
    ProductCategory,
    ProductType,
)
#from pay.service import init_app_pay


class TestView(TestCase):
    """
    Session variables difficult to test ref:
    http://stackoverflow.com/questions/4453764/how-do-i-modify-the-session-in-the-django-test-framework
    """

    def setUp(self):
        VatSettingsFactory()
        Notify.objects.create_notify('test@pkimber.net')
        default_scenario_login()
        #init_app_pay()
        self.web = get_user_web()
        self.assertTrue(self.client.login(
            username=self.web.username,
            password=TEST_PASSWORD,
        ))
        # create a payment
        stock = ProductType.objects.create_product_type('stock', 'Stock')
        stationery = ProductCategory.objects.create_product_category(
            'stationery', 'Stationery', stock
        )
        pencil = Product.objects.create_product(
            'pencil', 'Pencil', '', Decimal('1.32'), stationery
        )
        self.sales_ledger = SalesLedgerFactory(
            product=pencil,
            quantity=Decimal('2'),
        )
        # self.checkout = sales_ledger.create_checkout(token='123')
        # self.checkout.save()
        # self.checkout.url = reverse('pay.list')
        # self.checkout.url_failure = reverse('pay.list')
        # self.checkout.save()

    def _set_session_payment_pk(self, pk):
        session = self.client.session
        session[CHECKOUT_PK] = pk
        session.save()

    #def test_pay_later(self):
    #    self._set_session_payment_pk(self.checkout.pk)
    #    response = self.client.post(
    #        reverse('example.pay.later', kwargs=dict(pk=self.checkout.pk))
    #    )
    #    self.assertEqual(response.status_code, 302)
    #    self.assertIn('/pay/', response.url)

    def test_project_home(self):
        response = self.client.get(reverse('project.home'))
        self.assertEqual(response.status_code, 200)

    def test_stripe(self):
        self._set_session_payment_pk(self.sales_ledger.pk)
        response = self.client.get(
            reverse(
                'example.sales.ledger.checkout',
                kwargs=dict(pk=self.sales_ledger.pk)
            )
        )
        self.assertEqual(response.status_code, 200)
