# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('example_checkout', '__first__'),
        ('checkout', '0004_paymentplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(to='example_checkout.Contact')),
                ('payment_plan', models.ForeignKey(to='checkout.PaymentPlan')),
            ],
            options={
                'verbose_name': 'Contact payment plan',
                'verbose_name_plural': 'Contact payment plans',
                'ordering': ('contact__user__username', 'payment_plan__slug'),
            },
        ),
        migrations.CreateModel(
            name='ContactPlanPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('due', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('plan', models.ForeignKey(to='checkout.ContactPlan')),
            ],
            options={
                'verbose_name': 'Payments for a contact',
                'verbose_name_plural': 'Payments for a contact',
            },
        ),
    ]
