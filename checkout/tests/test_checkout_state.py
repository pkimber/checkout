# -*- encoding: utf-8 -*-
import pytest

from checkout.models import CheckoutState


@pytest.mark.django_db
def test_is_pending():
    assert not CheckoutState.objects.fail.is_pending
    assert CheckoutState.objects.pending.is_pending
    assert not CheckoutState.objects.request.is_pending
    assert not CheckoutState.objects.success.is_pending
