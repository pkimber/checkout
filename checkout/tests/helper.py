# -*- encoding: utf-8 -*-
from base.tests.model_maker import clean_and_save

from checkout.models import CheckoutError


def check_checkout(model_instance):
    """The 'StripeCheckout' model links to generic content."""
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
    model_instance.checkout_email
    model_instance.checkout_description
    model_instance.checkout_name
    model_instance.checkout_total
    model_instance.checkout_fail()
    model_instance.checkout_success()
    # model_instance.checkout_state
    # model_instance.set_checkout_state(CheckoutState.objects.success)
    url = model_instance.checkout_fail_url
    if not url:
        raise CheckoutError("{}.checkout_fail_url' should return a url")
    url = model_instance.checkout_success_url
    if not url:
        raise CheckoutError("{}.checkout_success_url' should return a url")
    # do we have mail templates for paid and pay later?
    # assert model_instance.mail_template_name
    # the generic content must implement 'get_absolute_url'
    model_instance.get_absolute_url()
    # the generic content must implement 'allow_pay_later'
    # model_instance.allow_pay_later()
    clean_and_save(model_instance)
