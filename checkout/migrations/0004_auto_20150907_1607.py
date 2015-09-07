# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_auto_20150903_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectpaymentplaninstalment',
            name='due',
            field=models.DateField(),
        ),
    ]
