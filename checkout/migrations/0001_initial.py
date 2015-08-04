# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('total', models.DecimalField(max_digits=8, null=True, blank=True, decimal_places=2)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('pk',),
                'verbose_name_plural': 'Checkouts',
                'verbose_name': 'Checkout',
            },
        ),
        migrations.CreateModel(
            name='CheckoutAction',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('payment', models.BooleanField()),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Checkout action',
                'verbose_name': 'Checkout action',
            },
        ),
        migrations.CreateModel(
            name='CheckoutInvoice',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('company_name', models.CharField(max_length=100, blank=True)),
                ('address_1', models.CharField(max_length=100, verbose_name='Address', blank=True)),
                ('address_2', models.CharField(max_length=100, verbose_name='', blank=True)),
                ('address_3', models.CharField(max_length=100, verbose_name='', blank=True)),
                ('town', models.CharField(max_length=100, blank=True)),
                ('county', models.CharField(max_length=100, blank=True)),
                ('postcode', models.CharField(max_length=20, blank=True)),
                ('country', models.CharField(max_length=100, blank=True)),
                ('contact_name', models.CharField(max_length=100, blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('checkout', models.OneToOneField(to='checkout.Checkout')),
            ],
            options={
                'ordering': ('email',),
                'verbose_name_plural': 'Checkout Invoices',
                'verbose_name': 'Checkout Invoice',
            },
        ),
        migrations.CreateModel(
            name='CheckoutState',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Checkout states',
                'verbose_name': 'Checkout state',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('customer_id', models.TextField()),
                ('expiry_date', models.DateField(null=True, blank=True)),
                ('refresh', models.BooleanField(help_text='Should the customer refresh their card details?', default=False)),
            ],
            options={
                'ordering': ('pk',),
                'verbose_name_plural': 'Customers',
                'verbose_name': 'Customer',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('total', models.DecimalField(max_digits=8, decimal_places=2)),
                ('deleted', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('created',),
                'verbose_name_plural': 'Object payment plans',
                'verbose_name': 'Object payment plan',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlanInstalment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField()),
                ('deposit', models.BooleanField(help_text='Is this the initial payment')),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('due', models.DateField(null=True, blank=True)),
                ('object_payment_plan', models.ForeignKey(to='checkout.ObjectPaymentPlan')),
                ('state', models.ForeignKey(to='checkout.CheckoutState', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Payments for an object',
                'verbose_name': 'Payments for an object',
            },
        ),
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
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
                'verbose_name_plural': 'Payment plan',
                'verbose_name': 'Payment plan',
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
            field=models.ForeignKey(to='checkout.Customer', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='checkout',
            name='state',
            field=models.ForeignKey(to='checkout.CheckoutState', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='checkout',
            name='user',
            field=models.ForeignKey(help_text='User who created the checkout request (or blank if the the user is not logged in)', to=settings.AUTH_USER_MODEL, related_name='+', null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='objectpaymentplaninstalment',
            unique_together=set([('object_payment_plan', 'count'), ('object_payment_plan', 'due')]),
        ),
        migrations.AlterUniqueTogether(
            name='objectpaymentplan',
            unique_together=set([('object_id', 'content_type')]),
        ),
    ]
