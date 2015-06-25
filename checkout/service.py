# -*- encoding: utf-8 -*-
from django.conf import settings

from mail.models import MailTemplate


# slug for the email template
#PAYMENT_LATER = 'payment_later'
#PAYMENT_THANKYOU = 'payment_thankyou'
#
#
#def init_app_pay():
#    """For the description, check 'mail_template_context' in 'pay.models'."""
#    MailTemplate.objects.init_mail_template(
#        PAYMENT_LATER,
#        'Thank you for your application',
#        (
#            "You can add the following variables to the template:\n"
#            "{{ name }} name of the customer.\n"
#            "{{ description }} transaction detail.\n"
#            "{{ total }} total value of the transaction."
#        ),
#        False,
#        settings.MAIL_TEMPLATE_TYPE,
#        subject='Thank you for your application',
#        description="We will contact you to arrange payment.",
#    )
#    MailTemplate.objects.init_mail_template(
#        PAYMENT_THANKYOU,
#        'Thank you for your payment',
#        (
#            "You can add the following variables to the template:\n"
#            "{{ name }} name of the customer.\n"
#            "{{ description }} transaction detail.\n"
#            "{{ total }} total value of the transaction."
#        ),
#        False,
#        settings.MAIL_TEMPLATE_TYPE,
#        subject='Thank you for your payment',
#        description="We will send you the course materials.",
#    )
