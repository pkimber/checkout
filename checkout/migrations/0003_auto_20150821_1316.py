# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import checkout.models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_auto_20150625_1159'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckoutSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('default_payment_plan', models.ForeignKey(to='checkout.PaymentPlan')),
            ],
            options={
                'verbose_name': 'Checkout Settings',
            },
        ),
        migrations.AlterField(
            model_name='checkout',
            name='state',
            field=models.ForeignKey(default=checkout.models.default_checkout_state, to='checkout.CheckoutState'),
        ),
        migrations.AlterField(
            model_name='objectpaymentplaninstalment',
            name='state',
            field=models.ForeignKey(default=checkout.models.default_checkout_state, to='checkout.CheckoutState'),
        ),
    ]
