# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_checkout_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('slug', models.SlugField(unique=True)),
                ('deposit_percent', models.IntegerField()),
                ('count', models.IntegerField()),
                ('interval_in_months', models.IntegerField()),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('slug',),
                'verbose_name': 'Payment plan',
                'verbose_name_plural': 'Payment plan',
            },
        ),
    ]
