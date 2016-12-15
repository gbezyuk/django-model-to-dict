=============================
Django-Model-To-Dict
=============================

.. image:: https://badge.fury.io/py/django-model-to-dict.png
    :target: https://badge.fury.io/py/django-model-to-dict

.. image:: https://travis-ci.org/gbezyuk/django-model-to-dict.png?branch=master
    :target: https://travis-ci.org/gbezyuk/django-model-to-dict

Django Model to Python dict serialization mixin.

Based on the original gist:
https://gist.github.com/gbezyuk/de29d4888818b87f8addd8143b5331e0

Requirements
------------

Currently the package is tested with Python3 and Django 1.10 only.

Documentation
-------------

The full documentation is at https://django-model-to-dict.readthedocs.io.

Quickstart
----------

Install Django-Model-To-Dict::

    pip install django-model-to-dict

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_model_to_dict.apps.DjangoModelToDictConfig',
        # or just 'django_model_to_dict'
        ...
    )

Use `ToDictMixin` with your model:

.. code-block:: python

    from django_model_to_dict.mixins import ToDictMixin
    from django.db import models


    class YourModel(models.Model, ToDictMixin):
        pass

Since now you model's instance have the `to_dict` method defined.

You can setup additional settings both in your global project configuration or in a particular model.
See docs for more details.

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
