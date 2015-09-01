# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse

from base.tests.test_utils import PermTestCase

from .factories import ObjectPaymentPlanInstalmentFactory


class TestViewPerm(PermTestCase):

    def setUp(self):
        self.setup_users()

    def test_list(self):
        self.assert_staff_only(reverse('checkout.list'))

    def test_list_audit(self):
        self.assert_staff_only(reverse('checkout.list.audit'))

    def test_object_payment_plan_instalment(self):
        obj = ObjectPaymentPlanInstalmentFactory()
        self.assert_staff_only(
            reverse('checkout.object.payment.plan.instalment', args=[obj.pk])
        )

    #def test_object_payment_plan_instalment_charge(self):
    #    obj = ObjectPaymentPlanInstalmentFactory()
    #    self.assert_staff_only(
    #        reverse('checkout.object.payment.plan.instalment.charge',
    #        args=[obj.pk]
    #        )
    #    )

    def test_object_payment_plan_card_expiry_list(self):
        self.assert_staff_only(
            reverse('checkout.object.payment.plan.card.expiry.list')
        )

    def test_object_payment_plan_list(self):
        self.assert_staff_only(reverse('checkout.object.payment.plan.list'))
