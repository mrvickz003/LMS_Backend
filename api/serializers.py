from rest_framework import serializers
from api.models import Form, FormData, FormFile, CustomUser
from django.utils.timezone import localtime


# Custom DateTime Field for desired formatting
class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        # Convert UTC to local timezone (IST) and format it
        ist_time = localtime(value)
        return ist_time.strftime("%d-%m-%Y %I:%M %p")


class CustomUserSerializer(serializers.ModelSerializer):
    last_login = CustomDateTimeField() 
    
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "photo",
            "password",
            "is_superuser",
            "is_active",
            "is_staff",
            "last_login",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }


# Form Serializer
class FormSerializer(serializers.ModelSerializer):
    create_date = CustomDateTimeField()
    update_date = CustomDateTimeField()

    class Meta:
        model = Form
        fields = [
            "id",
            "name",
            "layout",
            "create_at",
            "create_date",
            "update_at",
            "update_date",
        ]


# Form File Serializer
class FormFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFile
        fields = [
            "id", 
            "file", 
            "file_type"
        ]


# Form Data Serializer
class FormDataSerializer(serializers.ModelSerializer):
    create_date = CustomDateTimeField()
    update_date = CustomDateTimeField()
    files = FormFileSerializer(many=True, read_only=True)

    class Meta:
        model = FormData
        fields = [
            "id",
            "form",
            "submitted_data",
            "files",
            "create_at",
            "create_date",
            "update_at",
            "update_date",
        ]

    def validate(self, data):
        form = data.get("form")
        submitted_data = data.get("submitted_data")

        if not form or not submitted_data:
            raise serializers.ValidationError(
                "Form and submitted_data fields are required."
            )

        form_layout = form.layout.get("fields", [])
        errors = {}

        for field in form_layout:
            field_name = field["field_name"]
            field_type = field["type"]
            required = field.get("required", False)

            if required and field_name not in submitted_data:
                errors[field_name] = "This field is required."
            elif field_name in submitted_data:
                value = submitted_data[field_name]
                if field_type == "number" and not isinstance(value, int):
                    errors[field_name] = "This field must be a number."
                elif field_type == "email" and "@" not in value:
                    errors[field_name] = "This field must be a valid email."
                elif field_type == "dropdown" and value not in field.get("options", []):
                    errors[field_name] = f"Value must be one of {field.get('options')}."

        if errors:
            raise serializers.ValidationError(errors)

        return data
