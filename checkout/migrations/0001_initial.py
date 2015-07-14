# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('total', models.DecimalField(null=True, decimal_places=2, blank=True, max_digits=8)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Checkout',
                'verbose_name_plural': 'Checkouts',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='CheckoutAction',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Checkout action',
                'verbose_name_plural': 'Checkout action',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CheckoutState',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Checkout state',
                'verbose_name_plural': 'Checkout states',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ContactPaymentPlan',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=8)),
                ('object_id', models.PositiveIntegerField()),
                ('deleted', models.BooleanField(default=False)),
                ('contact', models.ForeignKey(to='contact.Contact')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Contact payment plan',
                'verbose_name_plural': 'Contact payment plans',
                'ordering': ('contact__user__username', 'payment_plan__slug'),
            },
        ),
        migrations.CreateModel(
            name='ContactPaymentPlanInstalment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('due', models.DateField(null=True, blank=True)),
                ('contact_payment_plan', models.ForeignKey(to='checkout.ContactPaymentPlan')),
                ('state', models.ForeignKey(null=True, to='checkout.CheckoutState', blank=True)),
            ],
            options={
                'verbose_name': 'Payments for a contact',
                'verbose_name_plural': 'Payments for a contact',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('customer_id', models.TextField()),
                ('expiry_date', models.DateField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                'verbose_name_plural': 'Payment plan',
                'ordering': ('slug',),
            },
        ),
        migrations.AddField(
            model_name='contactpaymentplan',
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
            field=models.ForeignKey(null=True, to='checkout.CheckoutState', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='contactpaymentplaninstalment',
            unique_together=set([('contact_payment_plan', 'due'), ('contact_payment_plan', 'count')]),
        ),
        migrations.AlterUniqueTogether(
            name='contactpaymentplan',
            unique_together=set([('object_id', 'content_type')]),
        ),
    ]
