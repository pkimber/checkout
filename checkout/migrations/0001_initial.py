# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Checkout',
                'ordering': ('pk',),
                'verbose_name_plural': 'Checkouts',
            },
        ),
        migrations.CreateModel(
            name='CheckoutAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Checkout action',
                'ordering': ('name',),
                'verbose_name_plural': 'Checkout action',
            },
        ),
        migrations.CreateModel(
            name='CheckoutState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Checkout state',
                'ordering': ('name',),
                'verbose_name_plural': 'Checkout states',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('customer_id', models.TextField()),
            ],
            options={
                'verbose_name': 'Customer',
                'ordering': ('pk',),
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.AddField(
            model_name='checkout',
            name='action',
            field=models.ForeignKey(to='checkout.CheckoutAction'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='customer',
            field=models.ForeignKey(to='checkout.Customer'),
        ),
    ]
