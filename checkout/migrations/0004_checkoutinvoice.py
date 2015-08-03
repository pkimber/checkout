# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_auto_20150722_1242'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckoutInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('company_name', models.CharField(blank=True, max_length=100)),
                ('address_1', models.CharField(verbose_name='Address', max_length=100, blank=True)),
                ('address_2', models.CharField(verbose_name='', max_length=100, blank=True)),
                ('address_3', models.CharField(verbose_name='', max_length=100, blank=True)),
                ('town', models.CharField(blank=True, max_length=100)),
                ('county', models.CharField(blank=True, max_length=100)),
                ('postcode', models.CharField(blank=True, max_length=20)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('contact_name', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('checkout', models.OneToOneField(to='checkout.Checkout')),
            ],
            options={
                'ordering': ('email',),
                'verbose_name_plural': 'Checkout Invoices',
                'verbose_name': 'Checkout Invoice',
            },
        ),
    ]
