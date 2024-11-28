from rest_framework import serializers
from .models import Form

class NestedFieldSerializer(serializers.Serializer):
    field_name = serializers.CharField(max_length=100)
    label = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=20)
    required = serializers.BooleanField()
    options = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    fields = serializers.ListField(child=serializers.DictField(), required=False)  # Nested fields for groups

class FormSerializer(serializers.ModelSerializer):
    layout = serializers.DictField(child=NestedFieldSerializer())  # Recursively handle nested fields in layout
    
    class Meta:
        model = Form
        fields = '__all__'
