# -*- encoding: utf-8 -*-
from django.test import TestCase

from checkout.management.commands import init_app_checkout


class TestCommand(TestCase):

    def test_init_app(self):
        """ Test the management command """
        command = init_app_checkout.Command()
        command.handle()
