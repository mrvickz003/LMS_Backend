# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Form
from api.serializers import FormSerializer

class FormView(APIView):
    # Retrieve all forms
    def get(self, request):
        forms = Form.objects.all()
        serializer = FormSerializer(forms, many=True)
        return Response(serializer.data)

    # Save a new form
    def post(self, request):
        serializer = FormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
