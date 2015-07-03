# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('example_checkout', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('total', models.DecimalField(decimal_places=2, null=True, max_digits=8, blank=True)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name_plural': 'Checkouts',
                'verbose_name': 'Checkout',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='CheckoutAction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Checkout action',
                'verbose_name': 'Checkout action',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CheckoutState',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Checkout states',
                'verbose_name': 'Checkout state',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ContactPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('contact', models.ForeignKey(to='example_checkout.Contact')),
            ],
            options={
                'verbose_name_plural': 'Contact payment plans',
                'verbose_name': 'Contact payment plan',
                'ordering': ('contact__user__username', 'payment_plan__slug'),
            },
        ),
        migrations.CreateModel(
            name='ContactPlanPayment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField()),
                ('due', models.DateField()),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('contact_plan', models.ForeignKey(to='checkout.ContactPlan')),
            ],
            options={
                'verbose_name_plural': 'Payments for a contact',
                'verbose_name': 'Payments for a contact',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('customer_id', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Customers',
                'verbose_name': 'Customer',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
                'verbose_name_plural': 'Payment plan',
                'verbose_name': 'Payment plan',
                'ordering': ('slug',),
            },
        ),
        migrations.AddField(
            model_name='contactplan',
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
        migrations.AlterUniqueTogether(
            name='contactplanpayment',
            unique_together=set([('contact_plan', 'due')]),
        ),
    ]
