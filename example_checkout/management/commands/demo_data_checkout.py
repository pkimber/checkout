# -*- encoding: utf-8 -*-
from decimal import Decimal

from django.core.management.base import BaseCommand

from example_checkout.models import (
    Contact,
    SalesLedger,
)
from finance.models import VatSettings
from login.tests.scenario import get_user_web
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
        contact = Contact.objects.create_contact(user=get_user_web())
        SalesLedger.objects.create_sales_ledger(
            contact, pencil, 2
        )
        SalesLedger.objects.create_sales_ledger(
            contact, pencil, 1
        )
        print("Created 'checkout' demo data...")
