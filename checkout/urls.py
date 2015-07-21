# -*- encoding: utf-8 -*-
from django.conf.urls import (
    patterns,
    url,
)

from .views import (
    CheckoutAuditListView,
    CheckoutListView,
    ObjectPaymentPlanInstalmentChargeUpdateView,
    ObjectPaymentPlanInstalmentDetailView,
    ObjectPaymentPlanListView,
    PaymentPlanCreateView,
    PaymentPlanDeleteView,
    PaymentPlanListView,
    PaymentPlanUpdateView,
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
    url(regex=r'^object/payment/plan/$',
        view=ObjectPaymentPlanListView.as_view(),
        name='checkout.object.payment.plan.list'
        ),
    url(regex=r'^object/payment/plan/instalment/(?P<pk>\d+)/$',
        view=ObjectPaymentPlanInstalmentDetailView.as_view(),
        name='checkout.object.payment.plan.instalment'
        ),
    url(regex=r'^object/payment/plan/instalment/(?P<pk>\d+)/charge/$',
        view=ObjectPaymentPlanInstalmentChargeUpdateView.as_view(),
        name='checkout.object.payment.plan.instalment.charge'
        ),
    url(regex=r'^payment/plan/$',
        view=PaymentPlanListView.as_view(),
        name='checkout.payment.plan.list'
        ),
    url(regex=r'^payment/plan/create/$',
        view=PaymentPlanCreateView.as_view(),
        name='checkout.payment.plan.create'
        ),
    url(regex=r'^payment/plan/(?P<pk>\d+)/delete/$',
        view=PaymentPlanDeleteView.as_view(),
        name='checkout.payment.plan.delete'
        ),
    url(regex=r'^payment/plan/(?P<pk>\d+)/update/$',
        view=PaymentPlanUpdateView.as_view(),
        name='checkout.payment.plan.update'
        ),
)
