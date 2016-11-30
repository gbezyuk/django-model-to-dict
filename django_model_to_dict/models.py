from .mixins import ToDictMixin
from .plugins.serialization.filebrowser_field import FilebrowserFieldSerializationPlugin

# TODO: extract to global settings, but still allow local in-class setting rewriting

class SampleToDictModel(ToDictMixin):
    TO_DICT_SERIALIZATION_PLUGINS = (FilebrowserFieldSerializationPlugin, )
    TO_DICT_SKIP_FIELDS = ('created', 'modified', 'is_enabled', 'order')
    TO_DICT_FIELD_GROUPING = {
        'contacts': ('tel', 'email', 'hyperlink')
    }
    TO_DICT_AUTOGROUPING_PREFIXES = ('price_',)

    def _default_related_fields_strategy(self, opts, data):
        related_fields = [f for f in opts.get_all_related_objects() if f.is_relation and f.multiple]
        for rf in related_fields:
            data[rf.name] = [i.to_dict() for i in getattr(self, rf.name).enabled()]
