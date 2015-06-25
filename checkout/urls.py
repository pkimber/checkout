# -*- encoding: utf-8 -*-
from django.conf.urls import (
    patterns,
    url,
)

from .views import (
    PaymentAuditListView,
    PaymentListView,
)


urlpatterns = patterns(
    '',
    url(regex=r'^audit/$',
        view=PaymentAuditListView.as_view(),
        name='pay.list.audit'
        ),
    url(regex=r'^$',
        view=PaymentListView.as_view(),
        name='pay.list'
        ),
)
