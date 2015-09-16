# -*- encoding: utf-8 -*-
from django.conf.urls import (
    patterns,
    url,
)

from .views import (
    #ObjectPaymentPlanInstalmentChargeUpdateView,
    CheckoutAuditListView,
    CheckoutCardRefreshListView,
    CheckoutListView,
    ObjectPaymentPlanCardExpiryListView,
    ObjectPaymentPlanDeleteView,
    ObjectPaymentPlanInstalmentDetailView,
    ObjectPaymentPlanInstalmentPaidUpdateView,
    ObjectPaymentPlanListView,
    PaymentPlanCreateView,
    PaymentPlanDeleteView,
    PaymentPlanListView,
    PaymentPlanUpdateView,
)


urlpatterns = patterns(
    '',
    url(regex=r'^$',
        view=CheckoutListView.as_view(),
        name='checkout.list'
        ),
    url(regex=r'^audit/$',
        view=CheckoutAuditListView.as_view(),
        name='checkout.list.audit'
        ),
    url(regex=r'^customer/card/refresh/$',
        view=CheckoutCardRefreshListView.as_view(),
        name='checkout.card.refresh.list'
        ),
    url(regex=r'^object/payment/plan/$',
        view=ObjectPaymentPlanListView.as_view(),
        name='checkout.object.payment.plan.list'
        ),
    url(regex=r'^object/payment/plan/(?P<pk>\d+)/delete/$',
        view=ObjectPaymentPlanDeleteView.as_view(),
        name='checkout.object.payment.plan.delete'
        ),
    url(regex=r'^object/payment/plan/card/expiry/$',
        view=ObjectPaymentPlanCardExpiryListView.as_view(),
        name='checkout.object.payment.plan.card.expiry.list'
        ),
    url(regex=r'^object/payment/plan/instalment/(?P<pk>\d+)/$',
        view=ObjectPaymentPlanInstalmentDetailView.as_view(),
        name='checkout.object.payment.plan.instalment'
        ),
    url(regex=r'^object/payment/plan/instalment/(?P<pk>\d+)/paid/$',
        view=ObjectPaymentPlanInstalmentPaidUpdateView.as_view(),
        name='checkout.object.payment.plan.instalment.paid'
        ),
    #url(regex=r'^object/payment/plan/instalment/(?P<pk>\d+)/charge/$',
    #    view=ObjectPaymentPlanInstalmentChargeUpdateView.as_view(),
    #    name='checkout.object.payment.plan.instalment.charge'
    #    ),
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
