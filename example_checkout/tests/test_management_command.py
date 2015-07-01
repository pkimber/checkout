# -*- encoding: utf-8 -*-
from django.test import TestCase

from checkout.management.commands import init_app_checkout
from login.management.commands import demo_data_login
from example_checkout.management.commands import demo_data_checkout


class TestCommand(TestCase):

    def test_demo_data(self):
        """ Test the management command """
        pre_command = demo_data_login.Command()
        pre_command.handle()
        pre_command = init_app_checkout.Command()
        pre_command.handle()
        command = demo_data_checkout.Command()
        command.handle()
