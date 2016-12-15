=====
Usage
=====

To use Django-Model-To-Dict in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_model_to_dict.apps.DjangoModelToDictConfig',
        ...
    )

Add Django-Model-To-Dict's URL patterns:

.. code-block:: python

    from django_model_to_dict import urls as django_model_to_dict_urls


    urlpatterns = [
        ...
        url(r'^', include(django_model_to_dict_urls)),
        ...
    ]
