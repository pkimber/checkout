# -*- encoding: utf-8 -*-
import logging

from celery import task

from checkout.models import ObjectPaymentPlanInstalment

logger = logging.getLogger(__name__)


@task()
def process_payments():
    logger.info('process_payments')
    ObjectPaymentPlanInstalment.objects.process_payments()


@task()
def refresh_card_expiry_dates():
    logger.info('refresh_card_expiry_dates')
    ObjectPaymentPlan.objects.refresh_card_expiry_dates()
