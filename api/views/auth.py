from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from api.serializers import CustomUserSerializer
from api.models import CustomUser, Company 
from api.views.common import OTPService
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
import random
from rest_framework.permissions import IsAuthenticated

# Create new user module 
@api_view(["POST"])
def register(request):
    company = request.data.get("company")
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name", "")
    mobile_number = request.data.get("mobile_number")
    if (
        not company
        or not first_name
        or not email
        or not password
        or not mobile_number
    ):
        return Response(
            {
                "error": "Company, First name, Email, password, and mobile number are required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
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
    if not OTPService.SendOTP(mobile_number):
        return Response(
            {"error": "Failed to send OTP."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    # Temporarily store the OTP and user details (use a more secure method in production)

    request.session["email"] = email
    request.session["password"] = password
    request.session["first_name"] = first_name
    request.session["last_name"] = last_name
    request.session["mobile_number"] = mobile_number
    request.session["company"] = company
    return Response(
        {"message": "OTP sent to your mobile number. Please verify."},
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
def account_verify(request):
    otp = request.data.get("otp")

    if not otp:
        return Response(
            {"error": "OTP is required for verification."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Retrieve stored data from the session
    email = request.session.get("email")
    password = request.session.get("password")
    first_name = request.session.get("first_name")
    last_name = request.session.get("last_name")
    mobile_number = request.session.get("mobile_number")
    company_name = request.session.get("company")

    if not email or not mobile_number:
        return Response(
            {"error": "No pending registration found. Please register again."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate OTP (replace this logic with your OTP verification mechanism)
    if not OTPService.VerifyOTP(mobile_number, otp):
        return Response(
            {"error": "Invalid OTP. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create a new user if OTP verification is successful
    try:
        # Ensure the company exists or create a new one
        company, created = Company.objects.get_or_create(name=company_name)

        # Create the user
        CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mobile_number=mobile_number,
            company=company,
        )

        # Send welcome email
        # send_welcome_email(email)

        # Clear session data after successful registration
        for key in ["email", "password", "first_name", "last_name", "mobile_number", "company"]:
            request.session.pop(key, None)

        # Return success response
        return Response(
            {"message": "Account successfully created."},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
# Login user 
@api_view(["POST"])
def user_login(request):
    identifier = request.data.get("email")  # This can be email or mobile number
    password = request.data.get("password")

    if not identifier or not password:
        return Response(
            {"error": "email or mobile number and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    if is_email:
        user = CustomUser.objects.filter(email=identifier).first()
    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()

    if user and user.check_password(password):  # Authenticate the user manually
        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "token": str(refresh.access_token),
                "userData": CustomUserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "Invalid ( email, mobile number ) or password."},
            status=status.HTTP_404_NOT_FOUND,
        )

@api_view(["POST"])
def forget_password_otp(request):
    identifier = request.data.get("identifier")
    if not identifier:
        return Response(
            {"error": "Identifier (email or mobile number) is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Check if identifier is email
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    # Handle Gmail OTP
    if is_email:
        user = CustomUser.objects.filter(email=identifier).first()
        if user:
            reset_token = random.randint(100000, 999999)
            send_mail(
                subject="Password Reset Request",
                message=f"Your password reset token is {reset_token}.",
                from_email="no-reply@example.com",  # Replace with your sender email
                recipient_list=[user.email],
            )
            # Store the reset token in session or temporary storage
            request.session["reset_token"] = reset_token
            return Response(
                {"message": f"A password reset token has been sent to {identifier}."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )
    
    # Handle Mobile Number OTP
    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()
        if user:
            otp = random.randint(100000, 999999)
            # Call the function to send OTP via Twilio or other services
            send_otp(identifier, otp)
            # Store OTP in session or temporary storage
            request.session["otp"] = otp
            return Response(
                {"message": f"A password reset OTP has been sent to {identifier}."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this mobile number."},
                status=status.HTTP_404_NOT_FOUND,
            )

# Verify Forget Password OTP
@api_view(["POST"])
def forget_password_otp_verify(request):
    identifier = request.data.get("identifier")
    otp = request.data.get("otp")

    if not identifier or not otp:
        return Response(
            {"error": "Identifier (email or mobile number) and OTP are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    # Verify Email-based OTP
    if is_email:
        user = CustomUser.objects.filter(email=identifier).first()
        if user and otp == str(request.session.get("reset_token")):
            return Response(
                {"message": "OTP verified successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid OTP or email."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    # Verify Mobile Number-based OTP
    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()
        if user and otp == str(request.session.get("otp")):
            return Response(
                {"message": "OTP verified successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid OTP or mobile number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

# Change Password (after OTP verification)
@api_view(["POST"])
def change_forget_password(request):
    identifier = request.data.get("identifier")
    password = request.data.get("password")
    confirm_password = request.data.get("confirmPassword")

    if not identifier or not password or not confirm_password:
        return Response(
            {"error": "Identifier, password, and confirm password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != confirm_password:
        return Response(
            {"error": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    if is_email:
        user = CustomUser.objects.filter(email=identifier).first()
        if user:
            user.set_password(password)
            user.save()
            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()
        if user:
            user.set_password(password)
            user.save()
            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this mobile number."},
                status=status.HTTP_404_NOT_FOUND,
            )        
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get("currentPassword")
    new_password = request.data.get("newPassword")
    confirm_password = request.data.get("confirmPassword")

    if not current_password or not new_password or not confirm_password:
        return Response(
            {"error": "All fields (currentPassword, newPassword, confirmPassword) are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user
    if not user.check_password(current_password):
        return Response(
            {"error": "Current password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != confirm_password:
        return Response(
            {"error": "New password and confirm password do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()

    return Response(
        {"message": "Password changed successfully."},
        status=status.HTTP_200_OK,
    )