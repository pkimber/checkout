Checkout
********

Django application for an online payments, payment plans and pay by invoice.

Install
=======

Virtual Environment
-------------------

::

  virtualenv --python=python3.4 venv-checkout
  source venv-checkout/bin/activate
  pip install --upgrade pip

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
