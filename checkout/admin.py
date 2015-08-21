# -*- encoding: utf-8 -*-
from django.contrib import admin

from .models import CheckoutSettings


class CheckoutSettingsAdmin(admin.ModelAdmin):
    pass

admin.site.register(CheckoutSettings, CheckoutSettingsAdmin)
