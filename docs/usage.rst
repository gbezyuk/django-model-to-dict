=====
Usage
=====

To use Django-Model-To-Dict in a project, add it to your `INSTALLED_APPS`:

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