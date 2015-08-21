# -*- encoding: utf-8 -*-
from decimal import Decimal

from django.core.management.base import BaseCommand

from checkout.models import (
    CheckoutSettings,
    ObjectPaymentPlan,
    PaymentPlan,
)
from contact.models import Contact
from example_checkout.models import SalesLedger
from finance.models import VatSettings
from login.tests.scenario import (
    get_user_staff,
    get_user_web,
)
from mail.models import Notify
from stock.models import (
    Product,
    ProductCategory,
    ProductType,
)


class Command(BaseCommand):

    help = "Create demo data for 'checkout'"

    def handle(self, *args, **options):
        vat_settings = VatSettings()
        vat_settings.save()
        Notify.objects.create_notify('test@pkimber.net')
        stock = ProductType.objects.create_product_type('stock', 'Stock')
        stationery = ProductCategory.objects.create_product_category(
            'stationery', 'Stationery', stock
        )
        pencil = Product.objects.create_product(
            'pencil', 'Pencil', '', Decimal('1.32'), stationery
        )
        contact_1 = Contact.objects.create_contact(user=get_user_web())
        SalesLedger.objects.create_sales_ledger(
            contact_1, pencil, 2
        )
        SalesLedger.objects.create_sales_ledger(
            contact_1, pencil, 1
        )
        contact_2 = Contact.objects.create_contact(user=get_user_staff())
        SalesLedger.objects.create_sales_ledger(
            contact_2, pencil, 6
        )
        payment_plan = PaymentPlan.objects.create_payment_plan(
            'default',
            'KB Payment Plan',
            Decimal('50'),
            2,
            1,
        )
        ObjectPaymentPlan.objects.create_object_payment_plan(
            contact_1,
            payment_plan,
            Decimal('1000'),
        )
        ObjectPaymentPlan.objects.create_object_payment_plan(
            contact_2,
            payment_plan,
            Decimal('400'),
        )
        # checkout settings
        checkout_settings = CheckoutSettings(default_payment_plan=payment_plan)
        checkout_settings.save()
        print("Created 'checkout' demo data...")
