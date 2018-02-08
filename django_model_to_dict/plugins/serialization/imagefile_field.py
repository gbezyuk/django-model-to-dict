from . import SerializationPlugin
from django.db.models import ImageField


class ImageFieldSerializationPlugin(SerializationPlugin):
    field_type = ImageField

    @staticmethod
    def serialize_field(field, model_instance):
        result = {}
        
        file_obj = field.value_from_object(model_instance)

        result = {
        	'url': file_obj.url,
        	'name': file_obj.name	
        }
        
        return result
