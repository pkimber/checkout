# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand

from checkout.models import ObjectPaymentPlan
from mail.models import MailTemplate


class Command(BaseCommand):

    help = "Initialise 'checkout' application"

    def handle(self, *args, **options):
        MailTemplate.objects.init_mail_template(
            ObjectPaymentPlan.MAIL_TEMPLATE_CARD_EXPIRY,
            'Re: Payment Plan - Card Expiry',
            (
                "You can add the following variables to the template:\n"
                "{{ candidate }} name of the candidate\n"
            ),
            False,
            settings.MAIL_TEMPLATE_TYPE,
            subject='Payment Plan - Card Expiry',
            description="Your card will expire soon...",
        )
        print("Initialised 'checkout' app...")
