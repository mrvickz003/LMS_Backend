from django.utils import timezone
from numpy import number
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from api.serializers import CustomUserSerializer
from api.models import CustomUser
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import base64
from django.contrib.auth import authenticate
from django.core.mail import send_mail
import random
from django.conf import settings

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

# User Registration
class Register(APIView):
    def post(self, request):
        company = request.data.get("company")
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name", "")
        mobile_number = request.data.get("mobile_number")

        if not company or not first_name or not email or not password or not mobile_number:
            return Response(
                {"error": "Company, First name, Email, password, and mobile number are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if CustomUser.objects.filter(email=email, mobile_number=mobile_number ).exists():
            return Response(
                {"error": "A user with this email or mobile number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Send the OTP to the mobile number (using a placeholder function)
        # Replace this with an actual SMS service like Twilio
        if not self.send_otp(mobile_number, otp):
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

    def send_otp(self, mobile_number, otp):
        print(f"Sending OTP {otp} to {mobile_number}")
        return True

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
            mobile_number=mobile_number, # Activate the user
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
        subject = "Welcome to Our Platform!"
        message = f"Hello {user.first_name},\n\nWelcome to our platform! We're excited to have you on board.\n\nBest regards,\nThe Team"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


@api_view(['POST'])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)
    if user is not None:
        user.last_login = timezone.now()
        user.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            "userData": CustomUserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    else:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
    
# Get Authenticated User Details
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def UserDetails(request):
    return Response({"user_data": CustomUserSerializer(request.user).data}, status=status.HTTP_200_OK)
