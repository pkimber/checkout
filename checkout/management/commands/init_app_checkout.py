# -*- encoding: utf-8 -*-
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Initialise 'checkout' application"

    def handle(self, *args, **options):
        print("Initialised 'checkout' app...")
