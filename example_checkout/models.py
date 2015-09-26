# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from checkout.models import CheckoutAction
from stock.models import Product


class SalesLedgerManager(models.Manager):

    def create_sales_ledger(self, contact, product, quantity):
        obj = self.model(
            contact=contact,
            product=product,
            quantity=quantity,
        )
        obj.save()
        return obj


class SalesLedger(models.Model):
    """List of prices."""

    contact = models.ForeignKey(settings.CONTACT_MODEL)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    objects = SalesLedgerManager()

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Sales ledger'
        verbose_name_plural = 'Sales ledger'

    def __str__(self):
        return '{}'.format(self.checkout_description)

    def get_absolute_url(self):
        """just for testing."""
        return reverse('project.home')

    @property
    def checkout_actions(self):
        return [
            CheckoutAction.CARD_REFRESH,
            CheckoutAction.INVOICE,
            CheckoutAction.PAYMENT,
            CheckoutAction.PAYMENT_PLAN,
        ]

    @property
    def checkout_can_charge(self):
        """We can always take a payment for this object!"""
        return True

    @property
    def checkout_name(self):
        return '{}'.format(self.contact.user.get_full_name())

    @property
    def checkout_description(self):
        result = '{} x {} @ {}'.format(
            self.product.name,
            self.quantity,
            self.product.price,
        )
        return [result]

    @property
    def checkout_email(self):
        return self.contact.user.email

    def checkout_fail(self):
        """Update the object to record the payment failure.

        Called from within a transaction so you can update the model.

        """
        pass

    def checkout_fail_url(self, checkout_pk):
        """just for testing."""
        return reverse('checkout.list.audit')

    def checkout_success(self, checkout):
        """Update the object to record the payment success.

        Called from within a transaction so you can update the model.

        """
        pass

    def checkout_success_url(self, checkout_pk):
        """just for testing."""
        return reverse(
            'example.sales.ledger.checkout.success',
            args=[checkout_pk]
        )

    @property
    def checkout_total(self):
        return self.product.price * self.quantity
