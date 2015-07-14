# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

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
    def checkout_name(self):
        return '{} {}'.format(
            self.contact.user.first_name,
            self.contact.user.last_name,
        )

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

    @property
    def checkout_fail(self):
        """Update the object to record the payment failure.

        Called from within a transaction and you can update the model.

        """
        pass

    @property
    def checkout_fail_url(self):
        """just for testing."""
        return reverse('checkout.list.audit')

    @property
    def checkout_success(self):
        """Update the object to record the payment success.

        Called from within a transaction and you can update the model.

        """
        pass

    @property
    def checkout_success_url(self):
        """just for testing."""
        return reverse('checkout.list')

    @property
    def checkout_total(self):
        return self.product.price * self.quantity
