# -*- encoding: utf-8 -*-
from django.conf.urls import (
    patterns,
    url,
)

from .views import (
    CheckoutAuditListView,
    CheckoutListView,
)


urlpatterns = patterns(
    '',
    url(regex=r'^audit/$',
        view=CheckoutAuditListView.as_view(),
        name='checkout.list.audit'
        ),
    url(regex=r'^$',
        view=CheckoutListView.as_view(),
        name='checkout.list'
        ),
)
