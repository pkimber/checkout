Checkout
********

Django application for an online payments.

Copied from:
https://github.com/pkimber/pay/tree/644-payment-plan-v2

For notes:
https://django-dev-and-deploy-using-salt.readthedocs.org/en/latest/app-pay.html
and
https://github.com/pkimber/docs/blob/master/source/app-pay.rst
and
https://github.com/pkimber/docs/blob/master/source/paypal.rst

Install
=======

Virtual Environment
-------------------

::

  pyvenv-3.4 --without-pip venv-checkout
  source venv-checkout/bin/activate
  wget https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py
  python get-pip.py

  pip install -r requirements/local.txt

Testing
=======

::

  find . -name '*.pyc' -delete
  py.test -x

Usage
=====

Add the following to your ``.private`` file::

  export MAIL_TEMPLATE_TYPE="django"
  export PAYPAL_RECEIVER_EMAIL="merchant@pkimber.net"
  export STRIPE_PUBLISH_KEY="your_stripe_publish_key"
  export STRIPE_SECRET_KEY="your_stripe_secret_key"

.. note:: Replace ``your_stripe_publish_key`` and ``your_stripe_secret_key``
          with the test versions of the *publishable* and *secret* key.

.. note:: The ``MAIL_TEMPLATE_TYPE`` should be selected from the list of
          constants at the top of the ``mail.models`` module.

::

  ../init_dev.sh

Release
=======

https://www.pkimber.net/open/
