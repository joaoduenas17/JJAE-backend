from rest_framework import serializers

class DynamicFieldsListSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsListSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

                
class DateRangeSerializer(serializers.Serializer):
    begin_date = serializers.DateField()
    end_date = serializers.DateField()


