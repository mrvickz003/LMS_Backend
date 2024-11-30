from rest_framework import serializers
from api.models import Form, FormData, FormFile,  CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['id', 'name', 'layout', 'create_at', 'create_date', 'update_at', 'update_date']

class FormFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFile
        fields = ['id', 'file', 'file_type']

class FormDataSerializer(serializers.ModelSerializer):
    files = FormFileSerializer(many=True, read_only=True)

    class Meta:
        model = FormData
        fields = ['id', 'form', 'submitted_data', 'files', 'create_at', 'create_date', 'update_at', 'update_date']

    def validate(self, data):
        form = data.get('form')
        submitted_data = data.get('submitted_data')

        if not form or not submitted_data:
            raise serializers.ValidationError("Form and submitted_data fields are required.")

        form_layout = form.layout.get('fields', [])
        errors = {}

        for field in form_layout:
            field_name = field['field_name']
            field_type = field['type']
            required = field.get('required', False)

            if required and field_name not in submitted_data:
                errors[field_name] = 'This field is required.'
            elif field_name in submitted_data:
                value = submitted_data[field_name]
                if field_type == 'number' and not isinstance(value, int):
                    errors[field_name] = 'This field must be a number.'
                elif field_type == 'email' and '@' not in value:
                    errors[field_name] = 'This field must be a valid email.'
                elif field_type == 'dropdown' and value not in field.get('options', []):
                    errors[field_name] = f"Value must be one of {field.get('options')}."

        if errors:
            raise serializers.ValidationError(errors)

        return data