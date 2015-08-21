# -*- encoding: utf-8 -*-
import pytest

from checkout.models import (
    CheckoutError,
    CheckoutSettings,
)
from checkout.tests.factories import CheckoutSettingsFactory


@pytest.mark.django_db
def test_factory():
    CheckoutSettingsFactory()


@pytest.mark.django_db
def test_settings():
    CheckoutSettingsFactory()
    CheckoutSettings.objects.settings()


@pytest.mark.django_db
def test_settings_none():
    with pytest.raises(CheckoutError) as e:
        CheckoutSettings.objects.settings()
    assert 'not been set-up in admin' in str(e.value)


@pytest.mark.django_db
def test_str():
    str(CheckoutSettingsFactory())
