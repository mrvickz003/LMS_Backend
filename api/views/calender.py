from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.models import Calendar
from api.serializers import CalendarSerializer
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_form(request):
    recurring_choices = dict(Calendar.RECURRING_CHOICES)
    event_type_choices = dict(Calendar.EVENT_TYPE)
    formsInputData = {
        'recurringChoices': [{'value': value, 'key':key} for key, value in recurring_choices.items()],
        'eventTypeChoices': [{'value': value, 'key':key} for key, value in event_type_choices.items()]
    }
    return Response({'formsInputData': formsInputData}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_events(request):
    company_id = request.query_params.get('company', None)
    filters = {'users': request.user}
    if company_id:
        filters['company'] = company_id
    events = Calendar.objects.filter(**filters).prefetch_related('users', 'company')
    if not events.exists():
        return Response({'detail': 'No events found for the current user.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CalendarSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    name = request.data.get('email')
    description = request.data.get('password')
    event_type = request.data.get('password')
    start_time = request.data.get('password')
    end_time = request.data.get('password')
    is_all_day = request.data.get('password')
    location = request.data.get('password')
    meeting_url = request.data.get('password')
    recurrence = request.data.get('password')
    users = request.data.get('password')
    
    """
    company
    create_by
    create_date
    update_by
    update_date
    """