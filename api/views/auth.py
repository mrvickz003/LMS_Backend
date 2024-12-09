from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from api.serializers import CustomUserSerializer
from api.models import CustomUser
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import base64
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from twilio.rest import Client
import random
from django.conf import settings
from django.template.loader import render_to_string

# Encrypt data
def encrypt_data(data, key):
    data_bytes = data.encode("utf-8")
    iv = os.urandom(16)  # Secure random IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode("utf-8")

# Decrypt data
def decrypt_data(encrypted_data, key):
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    iv = encrypted_data_bytes[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data_bytes[16:]) + decryptor.finalize()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data.decode("utf-8")

# API to get a secure random token
class GetToken(APIView):
    def get(self, request):
        key = os.urandom(32)
        random_token = os.urandom(16).hex()
        encrypted_token = encrypt_data(random_token, key)
        return Response({"token": encrypted_token}, status=status.HTTP_200_OK)
    
"""
def send_otp(mobile_number, otp):
    account_sid = "ACdff04487d1bc43ef8e5cc6ae114382fd"
    auth_token = "c6aa8244c675a479dac42b0f4d57dba7"
    twilio_phone_number = "+17753063489" 
    
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=twilio_phone_number,
            to=f"+91{mobile_number}",
        )
        return True
    except Exception as e:
        print(f"Failed to send OTP: {e}")
        return False
"""

def send_otp(mobile_number, otp):
        print(f"Sending OTP {otp} to {mobile_number}")
        return True
 
class Register(APIView):
    def post(self, request):
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

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Send the OTP to the mobile number (using a placeholder function)
        # Replace this with an actual SMS service like Twilio
        if not send_otp(mobile_number, otp):
            return Response(
                {"error": "Failed to send OTP."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Temporarily store the OTP and user details (use a more secure method in production)
        request.session["otp"] = otp
        request.session["email"] = email
        request.session["password"] = password
        request.session["first_name"] = first_name
        request.session["last_name"] = last_name
        request.session["mobile_number"] = mobile_number

        return Response(
            {"message": "OTP sent to your mobile number. Please verify."},
            status=status.HTTP_200_OK,
        )
   
class VerifyOtp(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        if not otp:
            return Response(
                {"error": "OTP is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check OTP from the session
        if int(otp) != request.session.get("otp", None):
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve user details from the session
        email = request.session.get("email")
        password = request.session.get("password")
        first_name = request.session.get("first_name")
        last_name = request.session.get("last_name")
        mobile_number = request.session.get("mobile_number")

        if not email or not password:
            return Response(
                {"error": "Session expired. Please register again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the user and activate them
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mobile_number=mobile_number,  # Activate the user
        )

        # Send a welcome email
        self.send_welcome_email(user)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "User verified and registered successfully.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


    def send_welcome_email(self, user):
        subject = "Welcome to LMS"
        html_message = render_to_string(
            'welcome_mail.html', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'current_year': 2024
            })
        from_email = "no-reply@example.com"
        recipient_list = [user.email]
        
        send_mail(subject, "", from_email, recipient_list, html_message=html_message)

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
            status=status.HTTP_401_UNAUTHORIZED,
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

    # Check if identifier is email or mobile number
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

    # Check if identifier is email
    try:
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    # Email-based password reset
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

    # Mobile number-based password reset
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