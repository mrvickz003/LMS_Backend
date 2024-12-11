from rest_framework.response import Response
from rest_framework import status
from api.models import CustomUser
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password

@api_view(["POST"])
def test_register(request):
    company = request.data.get("company")
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name", "")
    mobile_number = request.data.get("mobile_number")

    # Validate required fields
    if not company or not first_name or not email or not password or not mobile_number:
        return Response(
            {"error": "Company, First name, Email, password, and mobile number are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate mobile number range
    try:
        mobile_number = int(mobile_number)  # Ensure it's treated as an integer
        if mobile_number < 0 or mobile_number > 9999999999:
            raise ValueError
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid mobile number. It must be between 0 and 9999999999."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if email or mobile number already exists
    if CustomUser.objects.filter(email=email).exists():
        return Response(
            {"error": "A user with this email already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if CustomUser.objects.filter(mobile_number=mobile_number).exists():
        return Response(
            {"error": "A user with this mobile number already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create the user
    user = CustomUser.objects.create(
        email=email,
        password=make_password(password),  # Hash the password
        first_name=first_name,
        last_name=last_name,
        mobile_number=mobile_number,
    )

    return Response(
        {"message": "User verified and registered successfully."},
        status=status.HTTP_201_CREATED,
    )
