# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('checkout_date', models.DateTimeField()),
                ('description', models.TextField()),
                ('total', models.DecimalField(decimal_places=2, blank=True, max_digits=8, null=True)),
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
                ('payment', models.BooleanField()),
            ],
            options={
                'verbose_name': 'Checkout action',
                'ordering': ('name',),
                'verbose_name_plural': 'Checkout action',
            },
        ),
        migrations.CreateModel(
            name='CheckoutInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('company_name', models.CharField(max_length=100, blank=True)),
                ('address_1', models.CharField(verbose_name='Address', max_length=100, blank=True)),
                ('address_2', models.CharField(verbose_name='', max_length=100, blank=True)),
                ('address_3', models.CharField(verbose_name='', max_length=100, blank=True)),
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
                'verbose_name': 'Checkout Invoice',
                'ordering': ('email',),
                'verbose_name_plural': 'Checkout Invoices',
            },
        ),
        migrations.CreateModel(
            name='CheckoutSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Checkout Settings',
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
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('refresh', models.BooleanField(default=False, help_text='Should the customer refresh their card details?')),
            ],
            options={
                'verbose_name': 'Customer',
                'ordering': ('pk',),
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=8)),
                ('deleted', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Object payment plan',
                'ordering': ('created',),
                'verbose_name_plural': 'Object payment plans',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlanInstalment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField()),
                ('deposit', models.BooleanField(help_text='Is this the initial payment')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('due', models.DateField(blank=True, null=True)),
                ('object_payment_plan', models.ForeignKey(to='checkout.ObjectPaymentPlan')),
                ('state', models.ForeignKey(null=True, blank=True, to='checkout.CheckoutState')),
            ],
            options={
                'verbose_name': 'Payments for an object',
                'verbose_name_plural': 'Payments for an object',
            },
        ),
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                'verbose_name': 'Payment plan',
                'ordering': ('slug',),
                'verbose_name_plural': 'Payment plan',
            },
        ),
        migrations.AddField(
            model_name='objectpaymentplan',
            name='payment_plan',
            field=models.ForeignKey(to='checkout.PaymentPlan'),
        ),
        migrations.AddField(
            model_name='checkoutsettings',
            name='default_payment_plan',
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
            field=models.ForeignKey(null=True, blank=True, to='checkout.Customer'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='state',
            field=models.ForeignKey(null=True, blank=True, to='checkout.CheckoutState'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='user',
            field=models.ForeignKey(null=True, related_name='+', blank=True, to=settings.AUTH_USER_MODEL, help_text='User who created the checkout request (or blank if the the user is not logged in)'),
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
