from django.utils.timezone import make_aware
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.models import Calendar, CustomUser
from api.serializers import CalendarSerializer, CustomUserSerializer
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_form(request):
    try:
        # Get the recurring choices and event type choices from the Calendar model
        recurring_choices = dict(Calendar.RECURRING_CHOICES)
        event_type_choices = dict(Calendar.EVENT_TYPE)

        # Fetch users belonging to the same company as the logged-in user
        users_queryset = CustomUser.objects.filter(company=request.user.company)
        users_data = CustomUserSerializer(users_queryset, many=True).data

        # Structure the form input data
        forms_input_data = {
            'recurringChoices': [{'key': key, 'value': value} for key, value in recurring_choices.items()],
            'eventTypeChoices': [{'key': key, 'value': value} for key, value in event_type_choices.items()],
            'users': users_data,
        }

        # Return the response with the form data
        return Response({'formsInputData': forms_input_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    try:
        name = request.data.get('name')
        description = request.data.get('description')
        event_type = request.data.get('event_type')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        is_all_day = request.data.get('is_all_day')
        location = request.data.get('location')
        meeting_url = request.data.get('meeting_url')
        recurrence = request.data.get('recurrence')
        users = request.data.get('users', [])

        # Validate required fields
        if not name or not start_time or not end_time:
            return Response({"error": "Name, start_time, and end_time are required."}, status=400)

        # Parse start_time and end_time to datetime objects
        try:
            start_time = make_aware(datetime.strptime(start_time, "%d-%m-%Y %I:%M %p"))
            end_time = make_aware(datetime.strptime(end_time, "%d-%m-%Y %I:%M %p"))
        except ValueError:
            return Response({"error": "Invalid date format. Use 'DD-MM-YYYY HH:MM AM/PM'."}, status=400)

        # Create the event instance
        event = Calendar.objects.create(
            name=name,
            description=description,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            is_all_day=is_all_day,
            location=location,
            meeting_url=meeting_url,
            recurrence=recurrence,
            company=request.user.company,
            create_by=request.user,
            create_date=datetime.now(),
            update_by=request.user,
            update_date=datetime.now(),
        )

        # Add users to the event
        if users:
            user_instances = CustomUser.objects.filter(id__in=users)
            event.users.set(user_instances)

        # Serialize the event and return the response
        serializer = CalendarSerializer(event)
        return Response(serializer.data, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_event(request):
    try:
        event_id = request.data.get('id')
        if not event_id:
            return Response({"error": "Event ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        event = Calendar.objects.get(id=event_id)
        if event.company != request.user.company:
            return Response({"error": "You do not have permission to update this event."}, status=status.HTTP_403_FORBIDDEN)
        if event.create_by != request.user:
            return Response({"error": "You can only update events that you created."}, status=status.HTTP_403_FORBIDDEN)

        name = request.data.get('name', event.name)
        description = request.data.get('description', event.description)
        event_type = request.data.get('event_type', event.event_type)
        start_time = request.data.get('start_time', event.start_time)
        end_time = request.data.get('end_time', event.end_time)
        is_all_day = request.data.get('is_all_day', event.is_all_day)
        location = request.data.get('location', event.location)
        meeting_url = request.data.get('meeting_url', event.meeting_url)
        recurrence = request.data.get('recurrence', event.recurrence)
        users = request.data.get('users', [])

        if not name or not start_time or not end_time:
            return Response({"error": "Name, start_time, and end_time are required."}, status=400)
        try:
            start_time = make_aware(datetime.strptime(start_time, "%d-%m-%Y %I:%M %p"))
            end_time = make_aware(datetime.strptime(end_time, "%d-%m-%Y %I:%M %p"))
        except ValueError:
            return Response({"error": "Invalid date format. Use 'DD-MM-YYYY HH:MM AM/PM'."}, status=400)

        if users:
            user_instances = CustomUser.objects.filter(id__in=users)
            event.users.set(user_instances)

        # Update the event
        event.name = name
        event.description = description
        event.event_type = event_type
        event.start_time = start_time
        event.end_time = end_time
        event.is_all_day = is_all_day
        event.location = location
        event.meeting_url = meeting_url
        event.recurrence = recurrence
        event.update_by = request.user
        event.update_date = datetime.now()
        event.save()

        # Serialize the updated event and return the response
        serializer = CalendarSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Calendar.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_event(request):
    try:
        id = request.data.get('id')
        if not id:
            return Response({"error": "Event ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        event = Calendar.objects.get(id=id)
        if event.company != request.user.company:
            return Response({"error": "You do not have permission to delete this event."}, status=status.HTTP_403_FORBIDDEN)
        if event.create_by != request.user:
            return Response({"error": "You can only delete events that you created."}, status=status.HTTP_403_FORBIDDEN)
        event.delete()
        return Response({"detail": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Calendar.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)