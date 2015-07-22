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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('total', models.DecimalField(max_digits=8, null=True, blank=True, decimal_places=2)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name_plural': 'Checkouts',
                'ordering': ('pk',),
                'verbose_name': 'Checkout',
            },
        ),
        migrations.CreateModel(
            name='CheckoutAction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('payment', models.BooleanField()),
            ],
            options={
                'verbose_name_plural': 'Checkout action',
                'ordering': ('name',),
                'verbose_name': 'Checkout action',
            },
        ),
        migrations.CreateModel(
            name='CheckoutState',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Checkout states',
                'ordering': ('name',),
                'verbose_name': 'Checkout state',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('customer_id', models.TextField()),
                ('expiry_date', models.DateField(null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Customers',
                'ordering': ('pk',),
                'verbose_name': 'Customer',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlan',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('total', models.DecimalField(max_digits=8, decimal_places=2)),
                ('deleted', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Object payment plans',
                'ordering': ('created',),
                'verbose_name': 'Object payment plan',
            },
        ),
        migrations.CreateModel(
            name='ObjectPaymentPlanInstalment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField()),
                ('deposit', models.BooleanField(help_text='Is this the initial payment')),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('due', models.DateField(null=True, blank=True)),
                ('object_payment_plan', models.ForeignKey(to='checkout.ObjectPaymentPlan')),
                ('state', models.ForeignKey(null=True, to='checkout.CheckoutState', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Payments for an object',
                'verbose_name': 'Payments for an object',
            },
        ),
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                'verbose_name_plural': 'Payment plan',
                'ordering': ('slug',),
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
            field=models.ForeignKey(null=True, to='checkout.Customer', blank=True),
        ),
        migrations.AddField(
            model_name='checkout',
            name='state',
            field=models.ForeignKey(null=True, to='checkout.CheckoutState', blank=True),
        ),
        migrations.AddField(
            model_name='checkout',
            name='user',
            field=models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL, help_text='User who created the checkout request (or blank if the the user is not logged in)', blank=True),
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
