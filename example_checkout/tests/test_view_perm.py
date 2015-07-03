# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse

from base.tests.test_utils import PermTestCase


class TestViewPerm(PermTestCase):

    def setUp(self):
        self.setup_users()

    def test_checkout_list(self):
        self.assert_staff_only(reverse('checkout.list'))

    def test_checkout_list_audit(self):
        self.assert_staff_only(reverse('checkout.list.audit'))

    def test_checkout_contact_plan_list(self):
        self.assert_staff_only(reverse('checkout.contact.plan.list'))
