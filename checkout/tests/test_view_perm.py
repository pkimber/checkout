# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse

from base.tests.test_utils import PermTestCase

from .factories import PaymentPlanFactory


class TestViewPerm(PermTestCase):

    def setUp(self):
        self.setup_users()

    def test_payment_plan_create(self):
        self.assert_staff_only(reverse('checkout.payment.plan.create'))

    def test_payment_plan_delete(self):
        plan = PaymentPlanFactory()
        self.assert_staff_only(reverse('checkout.payment.plan.delete', args=[plan.pk]))

    def test_payment_plan_list(self):
        self.assert_staff_only(reverse('checkout.payment.plan.list'))

    def test_payment_plan_update(self):
        plan = PaymentPlanFactory()
        self.assert_staff_only(reverse('checkout.payment.plan.update', args=[plan.pk]))
