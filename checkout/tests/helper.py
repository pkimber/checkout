# -*- encoding: utf-8 -*-
from decimal import Decimal

from base.tests.model_maker import clean_and_save
from checkout.models import (
    CheckoutAction,
    CheckoutState,
)
from checkout.tests.factories import CheckoutFactory


def check_checkout(model_instance):
    """The 'Checkout' model links to generic content."""
    # @property list valid of actions e.g. ``return [CheckoutAction.PAYMENT]``
    model_instance.checkout_actions
    # @property check the model is in the correct state for taking payment
    model_instance.checkout_can_charge
    # @property the email address of the person who is paying
    model_instance.checkout_email
    # @property ``list`` of strings
    model_instance.checkout_description
    # method called on success, passing in the checkout action
    # model_instance.checkout_mail(CheckoutAction.objects.payment)
    # @property the name of the person who is paying
    model_instance.checkout_name
    # @property the total payment
    model_instance.checkout_total
    # ``method`` to update the object to record the payment failure.
    # Called from within a transaction so you can update the model.
    # Note: This method should update the ``model_instance`` AND ``save`` it.
    model_instance.checkout_fail()
    # method returning a url
    model_instance.checkout_fail_url(1)
    # Update the object to record the payment success.
    # Called from within a transaction so you can update the model.
    # Note: This method should update the ``model_instance`` AND ``save`` it.
    # We pass in the 'checkout' so the model instance can send an email etc.
    checkout = CheckoutFactory(
        action=CheckoutAction.objects.payment,
        content_object=model_instance,
        state=CheckoutState.objects.success,
        total=Decimal('123.45'),
    )
    model_instance.checkout_success(checkout)
    # method returning a url
    model_instance.checkout_success_url(1)
    model_instance.get_absolute_url()
    clean_and_save(model_instance)
    # old _____________________________________________________________________
    # can we create a payment instance (need to set url before save).
    # checkout = model_instance.create_checkout(token='123')
    #assert payment.paymentline_set.count() > 0, "no payment lines"
    #checkout.url = reverse('project.home')
    #checkout.url_failure = reverse('project.home')
    # clean_and_save(checkout)
    # can the generic content be paid?
    # required attributes
    # obj = model_instance.checkout('token')
    # if not type(obj) == Checkout:
    #     raise CheckoutError("{}.checkout' should create a 'Checkout' instance")
    # description = model_instance.checkout_description
    # if not type(description) == List:
    #     raise CheckoutError("{}.checkout_description' should create a 'List'")
    #actions = model_instance.checkout_actions
    #if not isinstance(actions, list):
    #    raise CheckoutError(
    #        "{}.checkout_actions' should return a list of "
    #        "checkout actions".format(model_instance.__class__.__name__)
    #    )
    # model_instance.checkout_state
    # model_instance.set_checkout_state(CheckoutState.objects.success)
    #if not url:
    #    raise CheckoutError("{}.checkout_fail_url' should return a url")
    #if not url:
    #    raise CheckoutError("{}.checkout_success_url' should return a url")
    # do we have mail templates for paid and pay later?
    # assert model_instance.mail_template_name
    # the generic content must implement 'allow_pay_later'
    # model_instance.allow_pay_later()
    # old _____________________________________________________________________
    # the generic content must implement 'get_absolute_url'


def check_object_payment_plan(model_instance):
    """The 'ObjectPaymentPlan' model links to generic content."""
    model_instance.checkout_email
    model_instance.checkout_name
