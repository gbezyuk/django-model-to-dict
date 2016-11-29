class SerializationPlugin:

    field_type = None

    @classmethod
    def check_field(cls, field):
        return type(field) == cls.field_type

    @staticmethod
    def serialize_field(field, model_instance):
        raise NotImplementedError
        