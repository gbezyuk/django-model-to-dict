from .settings import TO_DICT_PREFIXES, TO_DICT_PREFIX_SEPARATOR, TO_DICT_GROUPING,\
    TO_DICT_SERIALIZATION_PLUGINS, TO_DICT_SKIP, TO_DICT_POSTFIXES, TO_DICT_POSTFIX_SEPARATOR


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
    * postfix-based field grouping
    * serialization plugins for particular field types
    * related fields output
    * output compression


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


    ## Postfix-Based Field Grouping

    The same as mentioned above regarding prefixes works for postfixes, using `TO_DICT_POSTFIXES`
    and `TO_DICT_POSTFIX_SEPARATOR`.

    ```
    TO_DICT_POSTFIXES = ('_name',)
    ```

    This approach could be useful when dealing with translation like `first_name`, `last_name` => `name: first, last`.


    ## Serialization Plugins For Particular Field Types

    Django allows developers to use custom model field types, which may require specific serialization logic.
    Use Serialization Plugins for this purpose. Consider, you want to serialize information about django-filebrowser's
    image versions:

    ```
    TO_DICT_SERIALIZATION_PLUGINS = ('django_model_to_dict.plugins.serialization.FilebrowserFieldSerializationPlugin',)
    ```

    `TO_DICT_SERIALIZATION_PLUGINS` may be set in global settings or as a model property. It's empty by default.

    This feature is not covered with unit tests yet.


    ## Related Fields Output

    With `inspect_related_objects` argument specified to `True` (which is the default value), the serializer will
    also include information from `to_dict`-enabled related models. **Warning**: `related_name` is currently required.


    ## Output Compression

    There is a set of to_dict arguments which names are prefixed with `compress_`. These arguments control the way
    the serializer deals with empty values. Basically, when compression is on, empty values won't appear in the output;
    while with compression switched off they will be preserved.

    * `compress_fields`: ignore None fields on root level. Default: `True`.
    * `compress_groups`: ignore None fields inside manual groups. Default: `True`.
    * `compress_prefixes`: ignore None fields inside prefix groups. Default: `True`.
    * `compress_postfixes`: ignore None fields inside postfix groups. Default: `True`.
    * `compress_empty_groups`: ignore empty groups as a whole. Default: `False`.

    Not used yet:
    * `compress_empty_related_objects`: ignore empty or None values in related objects. Default: `False`.

    """

    def to_dict(self, compress_fields=True, compress_groups=True, compress_prefixes=True, compress_postfixes=True,
                compress_empty_groups=False, inspect_related_objects=True, compress_empty_related_objects=False,
                __ive_been_there_already=tuple()):
        """
        Serializes model's fields into a python dictionary.

        :param compress_fields: ignore None fields on root level
        :param compress_groups: ignore None fields inside manual groups
        :param compress_prefixes: ignore None fields inside prefix groups
        :param compress_postfixes: ignore None fields inside postfix groups
        :param compress_empty_groups: ignore empty groups as a whole
        :param inspect_related_objects: inspect related objects
        :param compress_empty_related_objects: ignore empty or None values in related objects
        :param __ive_been_there_already: private param to prevent infinite recursion

        :return: python dictionary representing serialized fields of the model
        """

        # the resulting dictionary
        result = {}

        fields_to_skip = getattr(self, 'TO_DICT_SKIP', TO_DICT_SKIP)

        # initializing manually specified field grouping
        self._init_grouping(result)

        # initializing prefix-based field grouping
        self._init_prefixes(result)

        # initializing postfix-based field grouping
        self._init_postfixes(result)

        # iterating over model's fields
        for field in self._meta.concrete_fields:

            # skipping explicitly specified fields
            if field.name in fields_to_skip:
                continue

            # handling prefixed fields grouping
            prefix = self._get_prefix(field.name)
            if prefix:
                prefix_key = self._clean_prefix(prefix)
                result[prefix_key][self._remove_prefix(field.name, prefix)] = self._handle_nontrivial_field(field) or field.value_from_object(self)
                continue

            # handling postfixed fields grouping
            postfix = self._get_postfix(field.name)
            if postfix:
                postfix_key = self._clean_postfix(postfix)
                result[postfix_key][self._remove_postfix(field.name, postfix)] = self._handle_nontrivial_field(field) or field.value_from_object(self)
                continue

            # handling manually specified field grouping
            group = self._get_group(field.name)
            if group:
                result[group][field.name] = self._handle_nontrivial_field(field) or field.value_from_object(self)
                continue
            # TODO: custom mapping

            result[field.name] = self._handle_nontrivial_field(field) or field.value_from_object(self)

        # setup empty values for None-valued fields
        if compress_fields:
            self._compress_fields(result)
        if compress_groups:
            self._compress_groups(result)
        if compress_prefixes:
            self._compress_prefixes(result)
        if compress_postfixes:
            self._compress_postfixes(result)
        if compress_empty_groups:
            self._compress_empty_groups(result)

        if inspect_related_objects:
            # there's a posibility to redefine the related fields strategy
            if hasattr(self, '_to_dict_related_fields_strategy'):
                self._to_dict_related_fields_strategy(result)
            else:
                self._default_related_fields_strategy(result)

        # calling pre_finish_hook if there is one
        if hasattr(self, '_to_dict_pre_finish_hook'):
            self._to_dict_pre_finish_hook(result)

        return result

    def _init_grouping(self, result):
        for prefix in getattr(self, 'TO_DICT_GROUPING', TO_DICT_GROUPING):
            result[prefix] = {}

    def _init_prefixes(self, result):
        for prefix in getattr(self, 'TO_DICT_PREFIXES', TO_DICT_PREFIXES):
            result[self._clean_prefix(prefix)] = {}

    def _init_postfixes(self, result):
        for postfix in getattr(self, 'TO_DICT_POSTFIXES', TO_DICT_POSTFIXES):
            result[self._clean_postfix(postfix)] = {}

    def _handle_nontrivial_field(self, field):

        serialization_plugins = getattr(self, 'TO_DICT_SERIALIZATION_PLUGINS', TO_DICT_SERIALIZATION_PLUGINS)

        for plugin in serialization_plugins:            
            if plugin.check_field(field):
                return plugin.serialize_field(field, self)
        return None

    def _default_related_fields_strategy(self, result):
        # TODO: better tests

        # before Django 1.10
        # related_fields = [f for f in self._meta.get_all_related_objects() if f.is_relation and f.multiple]
        # for rf in related_fields:
        #     result[rf.name] = [i.to_dict() for i in getattr(self, rf.name).all()]

        related_fields = [rf for rf in self._meta.get_fields() if rf.is_relation]
        for rf in related_fields:
            # TODO recursion using __ive_been_there_already to prevent stack overflow
            if rf.one_to_many:
                if not rf.related_name:
                    continue
                result[rf.related_name] = [
                    i.to_dict(inspect_related_objects=False) for i in getattr(self, rf.related_name).all()]
            if rf.many_to_one or rf.one_to_one:
                related_object = getattr(self, rf.name)
                if hasattr(related_object, 'to_dict'):
                    result[rf.name] = related_object.to_dict(inspect_related_objects=False)
            if rf.many_to_many:
                print('many_to_many', rf.name, rf)


    def _get_prefix(self, field_name):
        for prefix in getattr(self, 'TO_DICT_PREFIXES', TO_DICT_PREFIXES):
            if field_name.startswith(prefix):
                return prefix

    def _clean_prefix(self, prefix):
        separator = getattr(self, 'TO_DICT_PREFIX_SEPARATOR', TO_DICT_PREFIX_SEPARATOR)
        if prefix.endswith(separator):
            return prefix[:-len(separator)]
        return prefix

    def _get_postfix(self, field_name):
        for postfix in getattr(self, 'TO_DICT_POSTFIXES', TO_DICT_POSTFIXES):
            if field_name.endswith(postfix):
                return postfix

    def _clean_postfix(self, postfix):
        separator = getattr(self, 'TO_DICT_POSTFIX_SEPARATOR', TO_DICT_POSTFIX_SEPARATOR)
        if postfix.startswith(separator):
            return postfix[len(separator):]
        return postfix

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

    def _compress_postfixes(self, result):
        for postfix in getattr(self, 'TO_DICT_POSTFIXES', TO_DICT_POSTFIXES):
            postfix_key = self._clean_postfix(postfix)
            to_clear = []
            for field_name, field_value in result[postfix_key].items():
                if not field_value:
                    to_clear.append(field_name)
            for field_name in to_clear:
                del result[postfix_key][field_name]

    def _compress_empty_groups(self, result):
        # TODO: actually iterate over groups
        for k in [k for k in result if result[k] == {}]:
            del result[k]

    def _remove_prefix(self, field_name, prefix):
        if field_name.startswith(prefix):
            return field_name[len(prefix):]
        return field_name

    def _remove_postfix(self, field_name, postfix):
        if field_name.endswith(postfix):
            return field_name[:-len(postfix)]
        return field_name