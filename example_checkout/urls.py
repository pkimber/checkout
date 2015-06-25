# -*- encoding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

#from pay.views import pay_later_view

from .views import (
    ExampleCheckout,
    HomeView,
    #StripePaymentView,
    StripeUpdateView,
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
    url(regex=r'^example/checkout/(?P<pk>\d+)/$',
        view=ExampleCheckout.as_view(),
        name='example.checkout'
        ),
    #url(regex=r'^later/(?P<pk>\d+)/$',
    #    view=pay_later_view,
    #    name='example.pay.later'
    #    ),
    #url(regex=r'^stripe/payment/(?P<pk>\d+)/$',
    #    view=StripePaymentView.as_view(),
    #    name='example.stripe.payment'
    #    ),
    url(regex=r'^stripe/update/(?P<pk>\d+)/$',
        view=StripeUpdateView.as_view(),
        name='example.stripe.update'
        ),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#   ^ helper function to return a URL pattern for serving files in debug mode.
# https://docs.djangoproject.com/en/1.5/howto/static-files/#serving-files-uploaded-by-a-user

urlpatterns += staticfiles_urlpatterns()
