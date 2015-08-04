# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_auto_20150803_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='refresh',
            field=models.BooleanField(default=False, help_text='Should the customer refresh their card details?'),
        ),
    ]
