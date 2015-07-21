# -*- encoding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from .views import (
    ExampleRefreshExpiryDatesFormView,
    HomeView,
    SalesLedgerChargeUpdateView,
    SalesLedgerCheckoutUpdateView,
)

admin.autodiscover()


urlpatterns = patterns(
    '',
    url(regex=r'^$',
        view=HomeView.as_view(),
        name='project.home'
        ),
    url(regex=r'^$',
        view=HomeView.as_view(),
        name='project.settings'
        ),
    url(regex=r'^',
        view=include('login.urls')
        ),
    url(regex=r'^admin/',
        view=include(admin.site.urls)
        ),
    url(regex=r'^checkout/',
        view=include('checkout.urls')
        ),
    url(r'^home/user/$',
        view=RedirectView.as_view(url=reverse_lazy('project.home')),
        name='project.dash'
        ),
    url(regex=r'^example/refresh/card/expiry/dates/$',
        view=ExampleRefreshExpiryDatesFormView.as_view(),
        name='example.refresh.card.expiry.dates'
        ),
    url(regex=r'^sales/ledger/(?P<pk>\d+)/charge/$',
        view=SalesLedgerChargeUpdateView.as_view(),
        name='example.sales.ledger.charge'
        ),
    url(regex=r'^sales/ledger/(?P<pk>\d+)/checkout/$',
        view=SalesLedgerCheckoutUpdateView.as_view(),
        name='example.sales.ledger.checkout'
        ),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#   ^ helper function to return a URL pattern for serving files in debug mode.
# https://docs.djangoproject.com/en/1.5/howto/static-files/#serving-files-uploaded-by-a-user

urlpatterns += staticfiles_urlpatterns()
