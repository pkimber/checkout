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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('slug', models.SlugField(unique=True)),
                ('deposit', models.IntegerField(help_text='Initial deposit as a percentage')),
                ('count', models.IntegerField(help_text='Number of payments')),
                ('interval', models.IntegerField(help_text='Payment interval in months')),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Payment plan',
                'ordering': ('slug',),
                'verbose_name_plural': 'Payment plan',
            },
        ),
    ]
