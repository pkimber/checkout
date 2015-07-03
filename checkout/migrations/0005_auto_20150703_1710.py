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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(to='example_checkout.Contact')),
                ('payment_plan', models.ForeignKey(to='checkout.PaymentPlan')),
            ],
            options={
                'verbose_name_plural': 'Contact payment plans',
                'verbose_name': 'Contact payment plan',
                'ordering': ('contact__user__username', 'payment_plan__slug'),
            },
        ),
        migrations.CreateModel(
            name='ContactPlanPayment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('due', models.DateField()),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('plan', models.ForeignKey(to='checkout.ContactPlan')),
            ],
            options={
                'verbose_name_plural': 'Payments for a contact',
                'verbose_name': 'Payments for a contact',
            },
        ),
        migrations.AlterUniqueTogether(
            name='contactplanpayment',
            unique_together=set([('plan', 'due')]),
        ),
    ]
