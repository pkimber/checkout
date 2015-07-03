# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import checkout.models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_auto_20150625_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='state',
            field=models.ForeignKey(default=checkout.models.default_checkout_state, to='checkout.CheckoutState'),
        ),
        migrations.AddField(
            model_name='contactplanpayment',
            name='state',
            field=models.ForeignKey(default=checkout.models.default_checkout_state, to='checkout.CheckoutState'),
        ),
    ]
