# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse

from base.tests.test_utils import PermTestCase


class TestViewPerm(PermTestCase):

    def setUp(self):
        self.setup_users()

    def test_pay_list(self):
        self.assert_staff_only(reverse('pay.list'))

    def test_pay_list_audit(self):
        self.assert_staff_only(reverse('pay.list.audit'))
