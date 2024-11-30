from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from api.models import Form, CustomUser
from api.serializers import FormSerializer

class FormView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        forms = Form.objects.all()
        serializer = FormSerializer(forms, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data

        try:
            create_user = CustomUser.objects.get(id=data.get("create_at"))
            update_user = CustomUser.objects.get(id=data.get("update_at"))
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid user ID for create_at or update_at"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FormSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
