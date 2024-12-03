from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Calendar
from api.serializers import CalendarSerializer
from django.contrib.auth.models import AnonymousUser

@api_view(['GET'])
def get_events(request):
    if isinstance(request.user, AnonymousUser):
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    company = request.query_params.get('company', None)
    filters = {'users':request.user} # create_by or users
    if company:
        filters['company'] = company

    events = Calendar.objects.filter(**filters)

    if not events.exists():
        return Response({'detail': 'No events found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CalendarSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
