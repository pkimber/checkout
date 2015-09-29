# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand

from checkout.models import Customer
from mail.models import MailTemplate


class Command(BaseCommand):

    help = "Initialise 'checkout' application"

    def handle(self, *args, **options):
        MailTemplate.objects.init_mail_template(
            Customer.MAIL_TEMPLATE_CARD_EXPIRY,
            'Re: Card Expiry',
            (
                "You can add the following variables to the template:\n"
                "{{ name }} name of the customer\n"
            ),
            False,
            settings.MAIL_TEMPLATE_TYPE,
            subject='Card Expiry',
            description="Your card will expire soon...",
        )
        print("Initialised 'checkout' app...")
