# -*- encoding: utf-8 -*-
import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import transaction

from checkout.models import (
    CheckoutState,
    ObjectPaymentPlan,
    ObjectPaymentPlanInstalment,
)
from checkout.tests.factories import (
    CustomerFactory,
    ObjectPaymentPlanFactory,
    ObjectPaymentPlanInstalmentFactory,
    PaymentPlanFactory,
)
from checkout.tests.helper import check_checkout
from login.tests.factories import UserFactory
from .factories import ContactFactory


@pytest.mark.django_db
def test_can_charge_deposit():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        deposit=True,
        due=date.today(),
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.pending
    )
    assert obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_deposit_not_pending():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        deposit=True,
        due=date.today(),
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.request
    )
    assert not obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_due():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        due=date.today(),
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.request
    )
    assert obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_overdue():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        due=date.today()+relativedelta(days=-10),
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.request
    )
    assert obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_due_not_yet():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        due=date.today()+relativedelta(days=10),
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.request
    )
    assert not obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_fail():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.fail
    )
    assert not obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_not_deposit():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        due=date.today(),
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.pending
    )
    assert not obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_pending():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.pending
    )
    assert not obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_request():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.request
    )
    assert obj.checkout_can_charge


@pytest.mark.django_db
def test_can_charge_success():
    object_payment_plan = ObjectPaymentPlanFactory(
        content_object=ContactFactory()
    )
    obj = ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=object_payment_plan,
        state=CheckoutState.objects.success
    )
    assert not obj.checkout_can_charge


@pytest.mark.django_db
def test_check_checkout():
    with transaction.atomic():
        # this must be run within a transaction
        obj = ObjectPaymentPlan.objects.create_object_payment_plan(
            ContactFactory(),
            PaymentPlanFactory(),
            Decimal('100')
        )
    instalment = ObjectPaymentPlanInstalment.objects.get(
        object_payment_plan=obj
    )
    check_checkout(instalment)


@pytest.mark.django_db
def test_checkout_description():
    payment_plan = PaymentPlanFactory(
        name='pkimber',
        deposit=50,
        count=2,
        interval=1
    )
    # create the plan and the deposit
    contact_pp = ObjectPaymentPlan.objects.create_object_payment_plan(
        ContactFactory(),
        payment_plan,
        Decimal('100'),
    )
    # check deposit description
    deposit = ObjectPaymentPlanInstalment.objects.filter(
        object_payment_plan=contact_pp
    )
    assert 1 == deposit.count()
    assert [
        'pkimber', 'Deposit'
    ] == deposit[0].checkout_description
    # create the instalments
    contact_pp.create_instalments()
    # check
    instalments = ObjectPaymentPlanInstalment.objects.filter(
        object_payment_plan=contact_pp
    )
    assert 3 == instalments.count()
    assert [
        'pkimber', 'Instalment 2 of 3'
    ] == instalments[1].checkout_description


@pytest.mark.django_db
def test_checkout_fail():
    with transaction.atomic():
        # this must be run within a transaction
        obj = ObjectPaymentPlan.objects.create_object_payment_plan(
            ContactFactory(),
            PaymentPlanFactory(),
            Decimal('100')
        )
    obj = ObjectPaymentPlanInstalment.objects.get(
        object_payment_plan=obj
    )
    assert CheckoutState.objects.pending == obj.state
    obj.checkout_fail()
    assert CheckoutState.objects.fail == obj.state


@pytest.mark.django_db
def test_checkout_name():
    user = UserFactory(first_name='Patrick', last_name='Kimber')
    contact_pp = ObjectPaymentPlan.objects.create_object_payment_plan(
        ContactFactory(user=user),
        PaymentPlanFactory(),
        Decimal('100'),
    )
    obj = ObjectPaymentPlanInstalment.objects.get(
        object_payment_plan=contact_pp
    )
    assert 'Patrick Kimber' == obj.checkout_name


@pytest.mark.django_db
def test_checkout_success():
    contact_pp = ObjectPaymentPlan.objects.create_object_payment_plan(
        ContactFactory(),
        PaymentPlanFactory(),
        Decimal('100'),
    )
    obj = ObjectPaymentPlanInstalment.objects.get(
        object_payment_plan=contact_pp
    )
    assert CheckoutState.objects.pending == obj.state
    obj.checkout_success()
    assert CheckoutState.objects.success == obj.state


@pytest.mark.django_db
def test_checkout_total():
    payment_plan = PaymentPlanFactory(
        name='pkimber',
        deposit=50,
        count=2,
        interval=1
    )
    user = UserFactory(first_name='Patrick', last_name='Kimber')
    contact_pp = ObjectPaymentPlan.objects.create_object_payment_plan(
        ContactFactory(user=user),
        payment_plan,
        Decimal('100'),
    )
    contact_pp.create_instalments()
    assert Decimal('50') == ObjectPaymentPlanInstalment.objects.get(
        count=1
    ).checkout_total
    assert Decimal('25') == ObjectPaymentPlanInstalment.objects.get(
        count=2
    ).checkout_total
    assert Decimal('25') == ObjectPaymentPlanInstalment.objects.get(
        count=3
    ).checkout_total


@pytest.mark.django_db
def test_checkout_email():
    user = UserFactory(email='me@test.com')
    contact_pp = ObjectPaymentPlan.objects.create_object_payment_plan(
        ContactFactory(user=user),
        PaymentPlanFactory(),
        Decimal('100'),
    )
    obj = ObjectPaymentPlanInstalment.objects.get(
        object_payment_plan=contact_pp
    )
    assert 'me@test.com' == obj.checkout_email


#@pytest.mark.django_db
#def test_checkout_list():
#    c1 = CheckoutFactory(
#        action=CheckoutAction.objects.charge,
#        content_object=SalesLedgerFactory(),
#    )
#    c2 = CheckoutFactory(
#        action=CheckoutAction.objects.charge,
#        content_object=ObjectPaymentPlanInstalmentFactory(
#            object_payment_plan=ObjectPaymentPlanFactory(
#                content_object=ContactFactory(),
#            ),
#        ),
#    )
#    c3 = CheckoutFactory(
#        action=CheckoutAction.objects.charge,
#        content_object=ObjectPaymentPlanInstalmentFactory(
#            object_payment_plan=ObjectPaymentPlanFactory(
#                content_object=ContactFactory(),
#            ),
#        ),
#    )
#    checkout_list = ObjectPaymentPlanInstalment.objects.checkout_list
#    assert 2 == checkout_list.count()
#    assert c1 not in checkout_list
#    assert c2 in checkout_list
#    assert c3 in checkout_list


@pytest.mark.django_db
def test_due():
    today = date.today()
    ObjectPaymentPlanInstalmentFactory(
        count=1,
        due=today+relativedelta(days=-1),
        amount=Decimal('1'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        count=2,
        due=today+relativedelta(days=-2),
        amount=Decimal('2'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    result = [p.amount for p in ObjectPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('2')] == result


@pytest.mark.django_db
def test_due_plan_deleted():
    today = date.today()
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-1),
        amount=Decimal('1'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    object_payment_plan = ObjectPaymentPlanFactory(
        deleted=True,
        content_object=ContactFactory(),
    )
    ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=object_payment_plan,
        due=today+relativedelta(days=2),
        amount=Decimal('2'),
    )
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-3),
        amount=Decimal('3'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    result = [p.amount for p in ObjectPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_due_plan_deposit():
    today = date.today()
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-1),
        amount=Decimal('1'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        deposit=True,
        due=today+relativedelta(days=-2),
        amount=Decimal('2'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-3),
        amount=Decimal('3'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    result = [p.amount for p in ObjectPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_due_not_due():
    today = date.today()
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-1),
        amount=Decimal('1'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('2'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-3),
        amount=Decimal('3'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    result = [p.amount for p in ObjectPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_due_not_pending():
    today = date.today()
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-1),
        amount=Decimal('1'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-2),
        state=CheckoutState.objects.fail,
        amount=Decimal('2'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-3),
        amount=Decimal('3'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    result = [p.amount for p in ObjectPaymentPlanInstalment.objects.due]
    assert [Decimal('1'), Decimal('3')] == result


@pytest.mark.django_db
def test_factory():
    ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )


@pytest.mark.django_db
def test_create_instalments_first_of_month():
    obj = ObjectPaymentPlanInstalmentFactory(
        amount=Decimal('50'),
        count=1,
        deposit=True,
        due=date(2015, 3, 10),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    obj.object_payment_plan.create_instalments()
    assert date(2015, 3, 10) == ObjectPaymentPlanInstalment.objects.get(
        count=1
    ).due
    assert date(2015, 4, 1) == ObjectPaymentPlanInstalment.objects.get(
        count=2
    ).due
    assert date(2015, 5, 1) == ObjectPaymentPlanInstalment.objects.get(
        count=3
    ).due


@pytest.mark.django_db
def test_create_instalments_first_of_month_after_15th():
    obj = ObjectPaymentPlanInstalmentFactory(
        amount=Decimal('50'),
        count=1,
        deposit=True,
        due=date(2015, 3, 17),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    obj.object_payment_plan.create_instalments()
    assert date(2015, 3, 17) == ObjectPaymentPlanInstalment.objects.get(
        count=1
    ).due
    assert date(2015, 5, 1) == ObjectPaymentPlanInstalment.objects.get(
        count=2
    ).due
    assert date(2015, 6, 1) == ObjectPaymentPlanInstalment.objects.get(
        count=3
    ).due


@pytest.mark.django_db
def test_process_payments(mocker):
    """Process payments.

    I cannot get this to run as a test because I don't know how to create a
    test Stripe customer.

    """
    mocker.patch('stripe.Charge.create')
    mocker.patch('stripe.Customer.create')
    today = date.today()
    install_1 = ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=1),
        amount=Decimal('2'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    install_2 = ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-1),
        amount=Decimal('1'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    install_3 = ObjectPaymentPlanInstalmentFactory(
        due=today+relativedelta(days=-2),
        amount=Decimal('2'),
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    )
    CustomerFactory(
        email=install_2.object_payment_plan.content_object.checkout_email
    )
    CustomerFactory(
        email=install_3.object_payment_plan.content_object.checkout_email
    )
    ObjectPaymentPlanInstalment.objects.process_payments()
    # check
    install_1.refresh_from_db()
    assert install_1.state == CheckoutState.objects.pending
    install_2.refresh_from_db()
    assert install_2.state == CheckoutState.objects.success
    install_3.refresh_from_db()
    assert install_3.state == CheckoutState.objects.success


@pytest.mark.django_db
def test_str():
    str(ObjectPaymentPlanInstalmentFactory(
        object_payment_plan=ObjectPaymentPlanFactory(
            content_object=ContactFactory(),
        ),
    ))
