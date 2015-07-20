# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('description', models.TextField()),
                ('total', models.DecimalField(max_digits=8, blank=True, null=True, decimal_places=2)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('pk',),
                'verbose_name': 'Checkout',
                'verbose_name_plural': 'Checkouts',
            },
        ),
        migrations.CreateModel(
            name='CheckoutAction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('payment', models.BooleanField()),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Checkout action',
                'verbose_name_plural': 'Checkout action',
            },
        ),
        migrations.CreateModel(
            name='CheckoutState',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Checkout state',
                'verbose_name_plural': 'Checkout states',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('customer_id', models.TextField()),
                ('expiry_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('pk',),
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('total', models.DecimalField(max_digits=8, decimal_places=2)),
                ('deleted', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('created',),
                'verbose_name': 'Object payment plan',
                'verbose_name_plural': 'Object payment plans',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlanInstalment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField()),
                ('deposit', models.BooleanField(help_text='Is this the initial payment')),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('due', models.DateField(blank=True, null=True)),
                ('object_payment_plan', models.ForeignKey(to='checkout.ObjectPaymentPlan')),
                ('state', models.ForeignKey(to='checkout.CheckoutState', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Payments for an object',
                'verbose_name_plural': 'Payments for an object',
            },
        ),
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('slug', models.SlugField(unique=True)),
                ('deposit', models.IntegerField(help_text='Initial deposit as a percentage')),
                ('count', models.IntegerField(help_text='Number of instalments')),
                ('interval', models.IntegerField(help_text='Instalment interval in months')),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('slug',),
                'verbose_name': 'Payment plan',
                'verbose_name_plural': 'Payment plan',
            },
        ),
        migrations.AddField(
            model_name='objectpaymentplan',
            name='payment_plan',
            field=models.ForeignKey(to='checkout.PaymentPlan'),
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
        migrations.AddField(
            model_name='checkout',
            name='state',
            field=models.ForeignKey(to='checkout.CheckoutState', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='checkout',
            name='user',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='objectpaymentplaninstalment',
            unique_together=set([('object_payment_plan', 'due'), ('object_payment_plan', 'count')]),
        ),
        migrations.AlterUniqueTogether(
            name='objectpaymentplan',
            unique_together=set([('object_id', 'content_type')]),
        ),
    ]
