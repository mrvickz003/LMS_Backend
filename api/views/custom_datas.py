from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import FormData, Form
from api.serializers import FormDataSerializer
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from api.models import FormFile

@api_view(['POST'])
def submit_form_data(request):
    if request.method == 'POST':
        # Check if the user is authenticated
        if isinstance(request.user, AnonymousUser):
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        form_id = request.data.get('form')
        try:
            # Retrieve the form by ID
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response(
                {"error": "Form not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        submitted_data = request.data.get('submitted_data')
        files = request.FILES

        # Create FormData object with authenticated user
        form_data = FormData.objects.create(
            form=form,  # Use the retrieved form object
            submitted_data=submitted_data,
            create_at=request.user,  # Use authenticated user
            create_date=timezone.now(),
            update_at=request.user,  # Use authenticated user
            update_date=timezone.now(),
        )

        # Process each file (file keys should be in the format 'photo_1', 'audio_1', etc.)
        for file_key, file in files.items():
            file_type = file_key.split('_')[0]  # Assuming the file field names are like 'photo_1', 'audio_1', etc.
            FormFile.objects.create(
                file=file,
                file_type=file_type,
                form_submission=form_data,
            )

        # Serialize the response
        serializer = FormDataSerializer(form_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_form_data(request, form_data_id):
    # Retrieve form data by ID
    form_data = get_object_or_404(FormData, id=form_data_id)

    # Serialize the form data
    serializer = FormDataSerializer(form_data)
    return Response(serializer.data, status=status.HTTP_200_OK)
