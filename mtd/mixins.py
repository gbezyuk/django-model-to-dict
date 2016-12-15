from .settings import TO_DICT_PREFIXES, TO_DICT_PREFIX_SEPARATOR, TO_DICT_GROUPING,\
    TO_DICT_SERIALIZATION_PLUGINS, TO_DICT_SKIP


class ToDictMixin:
    """
    This mixin adds 'to_dict()' method to your model, which iterates
    over model's fields and saves them into a python dictionary.

    This method is first of all intended for custom API JSON serializations.


    ## Remarkable features

    There are some additional features available:
    * skipping fields
    * manual field grouping
    * prefix-based field grouping
    * serialization plugins for particular field types


    ## Skipping Fields

    Probably you wouldn't want to store every field of the original model in your dictionary serialization.
    Use `TO_DICT_SKIP` to skip some fields (consider it a blacklist).

    ```
    TO_DICT_SKIP = ('id', 'created_at', 'modified_at', 'is_enabled')
    ```

    This configuration parameter may be set in global settings or as a model property. It's empty by default.


    ## Manual Field Grouping

    Consider you have a model of a `Person` with fields `name`, `tel` and `email`, and you want to represent
    it grouping `tel` and `email` together under 'contacts' key. This goal can be achieved using manual field
    grouping with `TO_DICT_GROUPING` configuration param:

    ```
    TO_DICT_GROUPING = {
        'contacts': ('tel', 'email')
    }
    ```

    The resulting dictionary will have this structure:
    ```
    {
        'name': 'Some Name',
        'contacts': {
            'tel': '555-55-55',
            'email': 'mail@example.com'
        }
    }
    ```

    As usual, `TO_DICT_GROUPING` may be set in global settings or as a model property. It's empty by default.


    ## Prefix-Based Field Grouping

    Consider you have a model for some `Product` with fields `name`, `price_base`, `price_discount`, `price_currency`.
    Maybe you'll want to group price-related fields under `price` key in your representation. Using manual grouping
    for this purpose is possible yet would be slightly verbose. We can do better using prefix-based field grouping.

    ```
    TO_DICT_PREFIXES = ('price_',)
    ```

    All we need is to specify the prefix (and maybe the prefix separator, which is `_` by default).
    The result would look like:

    ```
    {
        'name': 'Some Product',
        'price': {
            'base': 99,
            'discount': 79,
            'currency': 'USD'
        }
    }
    ```

    The prefixes are supposed to end with a separator character(s). If you use a separator other than default '_',
    specify it using `TO_DICT_PREFIX_SEPARATOR`. `TO_DICT_SERIALIZATION_PLUGINS` may be set in global settings or
    as a model property. It's empty by default.


    ## Serialization Plugins For Particular Field Types

    Django allows developers to use custom model field types, which may require specific serialization logic.
    Use Serialization Plugins for this purpose. Consider, you want to serialize information about django-filebrowser's
    image versions:

    ```
    TO_DICT_SERIALIZATION_PLUGINS = ('model_to_dict.plugins.serialization.FilebrowserFieldSerializationPlugin', )
    ```

    `TO_DICT_SERIALIZATION_PLUGINS` may be set in global settings or as a model property. It's empty by default.


    """

    def to_dict(self, compress_fields=True, compress_groups=True, compress_prefixes=True):
        """
        Serializes model's fields into a python dictionary.

        :return: python dictionary representing serialized fields of the model
        """

        # the resulting dictionary
        result = {}

        fields_to_skip = getattr(self, 'TO_DICT_SKIP', TO_DICT_SKIP)

        # initializing manually specified field grouping
        self._init_grouping(result)

        # initializing prefix-based field grouping
        self._init_prefixes(result)

        # iterating over model's fields
        for field in self._meta.concrete_fields:

            # skipping explicitly specified fields
            if field.name in fields_to_skip:
                continue

            # handling prefixed fields grouping
            prefix = self._get_prefix(field.name)
            if prefix:
                prefix_key = self._clean_prefix(prefix)
                result[prefix_key][field.name.replace(prefix, '')] = field.value_from_object(self)
                continue

            # handling manually specified field grouping
            group = self._get_group(field.name)
            if group:
                result[group][field.name] = field.value_from_object(self)
                continue

            # handling images and other non-trivial files
            # if self._handle_nontrivial_field(field, result):
            #     continue

            # handling default case
            result[field.name] = field.value_from_object(self)

        # setup empty values for None-valued fields
        if compress_fields:
            self._compress_fields(result)
        if compress_groups:
            self._compress_groups(result)
        if compress_prefixes:
            self._compress_prefixes(result)

        # cleanup for unused grouping
        # for k in [k for k in result if result[k] == {}]:
        #     del result[k]

        # the mixin allows to redefine the related fields strategy
        # if hasattr(self, '_to_dict_related_fields_strategy'):
        #     self._to_dict_related_fields_strategy(result)
        # else:
        #     self._default_related_fields_strategy(result)

        # calling pre_finish_hook if exists
        # if hasattr(self, '_to_dict_pre_finish_hook'):
        #     self._to_dict_pre_finish_hook(result)

        return result

    def _init_grouping(self, result):
        for prefix in getattr(self, 'TO_DICT_GROUPING', TO_DICT_GROUPING):
            result[prefix] = {}

    def _init_prefixes(self, result):
        for prefix in getattr(self, 'TO_DICT_PREFIXES', TO_DICT_PREFIXES):
            result[self._clean_prefix(prefix)] = {}

    def _handle_nontrivial_field(self, field, data):

        serialization_plugins = getattr(self, 'TO_DICT_SERIALIZATION_PLUGINS', TO_DICT_SERIALIZATION_PLUGINS)

        for plugin in serialization_plugins:
            if plugin.check_field(field):
                data[field.name] = plugin.serialize_field(field, self)
                return True
        return False

    def _default_related_fields_strategy(self, data):
        related_fields = [f for f in self._meta.get_all_related_objects() if f.is_relation and f.multiple]
        for rf in related_fields:
            data[rf.name] = [i.to_dict() for i in getattr(self, rf.name).all()]

    def _get_prefix(self, field_name):
        for prefix in getattr(self, 'TO_DICT_PREFIXES', TO_DICT_PREFIXES):
            if field_name.startswith(prefix):
                return prefix

    def _clean_prefix(self, prefix):
        # TODO: strip at the end only
        return prefix.replace(getattr(self, 'TO_DICT_PREFIX_SEPARATOR', TO_DICT_PREFIX_SEPARATOR), '')

    def _get_group(self, field_name):
        for group, group_cfg in (getattr(self, 'TO_DICT_GROUPING', TO_DICT_GROUPING)).items():
            if field_name in group_cfg:
                return group

    def _compress_fields(self, result):
        to_clear = []
        for field_name, field_value in result.items():
            if not field_value:
                to_clear.append(field_name)
        for field_name in to_clear:
            del result[field_name]

    def _compress_groups(self, result):
        for group in (getattr(self, 'TO_DICT_GROUPING', TO_DICT_GROUPING)).keys():
            to_clear = []
            for field_name, field_value in result[group].items():
                if not field_value:
                    to_clear.append(field_name)
            for field_name in to_clear:
                del result[group][field_name]

    def _compress_prefixes(self, result):
        for prefix in getattr(self, 'TO_DICT_PREFIXES', TO_DICT_PREFIXES):
            prefix_key = self._clean_prefix(prefix)
            to_clear = []
            for field_name, field_value in result[prefix_key].items():
                if not field_value:
                    to_clear.append(field_name)
            for field_name in to_clear:
                del result[prefix_key][field_name]
