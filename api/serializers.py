from rest_framework import serializers
from api.models import Form, FormData, FormFile, CustomUser, Calendar, Company
from django.utils.timezone import localtime
import base64
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Check if data is a base64 string
        if isinstance(data, str) and data.startswith('data:image'):
            # Extract the base64 string from the data
            format, imgstr = data.split(';base64,')  # split into format and base64 string
            img_data = base64.b64decode(imgstr)  # decode the base64 string into bytes
            image = Image.open(BytesIO(img_data))  # open the image using PIL

            # Save image as InMemoryUploadedFile
            file_name = "uploaded_image.jpg"  # you can customize the filename
            image_file = BytesIO()
            image.save(image_file, format='JPEG')
            image_file.seek(0)

            return InMemoryUploadedFile(
                image_file, None, file_name, 'image/jpeg', image_file.tell(), None
            )
        else:
            # If it's not a base64 string, pass to the original ImageField behavior
            return super().to_internal_value(data)
    
    def to_representation(self, value):
        # Convert the image to a base64 string to be returned in the response
        if value:
            with open(value.path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{image_data}"
        return None

class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        ist_time = localtime(value)
        return ist_time.strftime("%d-%m-%Y %I:%M %p")

# Company Serializer
class CompanySerializers(serializers.ModelSerializer):
    create_date = CustomDateTimeField()
    update_date = CustomDateTimeField()
    # update_by = CustomUserSerializer(read_only=True)
    # update_by = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id',
            'company_name',
            'create_by',
            'create_date',
            'update_by',
            'update_date'
        ]
        read_only_fields = ['id', 'create_date', 'update_date']

# Usage in your serializer
class CustomUserSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "company",
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "photo",  # Use the base64 image field
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
    update_by = CustomUserSerializer(read_only=True)
    update_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = Form
        fields = [
            "id",
            "name",
            "layout",
            "create_by",
            "create_date",
            "update_by",
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
    update_by = CustomUserSerializer(read_only=True)
    update_by = CustomUserSerializer(read_only=True)
    files = FormFileSerializer(many=True, read_only=True)

    class Meta:
        model = FormData
        fields = [
            "id",
            "form",
            "submitted_data",
            "files",
            "create_by",
            "create_date",
            "update_by",
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

class CalendarSerializer(serializers.ModelSerializer):
    company = CompanySerializers(read_only=True)
    start_time = CustomDateTimeField()
    end_time = CustomDateTimeField()
    create_date = CustomDateTimeField()
    update_date = CustomDateTimeField()
    update_by = CustomUserSerializer(read_only=True)
    users = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = Calendar
        fields = [
            'id',
            'company',
            'name',
            'description',
            'event_type',
            'start_time',
            'end_time',
            'is_all_day',
            'location',
            'meeting_url',
            'recurrence',
            'users',
            'create_by',
            'create_date',
            'update_by',
            'update_date',
        ]
        read_only_fields = ['id', 'create_date', 'update_date']