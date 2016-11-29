from filebrowser.fields import FileBrowseField
from filebrowser.settings import VERSIONS as FILEBROWSER_VERSIONS


class SerializationPlugin:

    field_type = None

    @classmethod
    def check_field(cls, field):
        return type(field) == cls.field_type

    @staticmethod
    def serialize_field(field, model_instance):
        raise NotImplementedError


class FilebrowserFieldSerializationPlugin(SerializationPlugin):
    field_type = FileBrowseField

    @staticmethod
    def serialize_field(field, model_instance):
        result = {}
        try:
            file_obj = field.value_from_object(model_instance)
            if file_obj:
                result['original'] = file_obj.url
                for version in FILEBROWSER_VERSIONS:
                    result[version] = file_obj.version_generate(version).url
        except FileNotFoundError:
            result['error'] = 'file not found'
        return result
        