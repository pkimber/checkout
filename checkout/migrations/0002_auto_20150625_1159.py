# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def _init_state(model, name, slug):
    try:
        model.objects.get(slug=slug)
    except model.DoesNotExist:
        instance = model(**dict(name=name, slug=slug))
        instance.save()
        instance.full_clean()


def _init_state_action(model, name, slug, payment):
    try:
        obj = model.objects.get(slug=slug)
    except model.DoesNotExist:
        instance = model(**dict(name=name, slug=slug, payment=payment))
        instance.save()
        instance.full_clean()


def default_state(apps, schema_editor):
    """Create default states.

    We can't import a model directly as it may be a newer version than this
    migration expects.  We use the historical version.

    """
    model = apps.get_model('checkout', 'CheckoutAction')
    _init_state_action(model, 'Payment', 'payment', True)
    _init_state_action(model, 'Setup Payment Plan', 'payment_plan', False)
    _init_state_action(model, 'Update Card', 'card_update', False)

    model = apps.get_model('checkout', 'CheckoutState')
    _init_state(model, 'Fail', 'fail')
    _init_state(model, 'Pending', 'pending')
    _init_state(model, 'Request', 'request')
    _init_state(model, 'Success', 'success')


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(default_state),
    ]
