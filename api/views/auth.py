from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import get_authorization_header
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from api.serializers import CustomUserSerializer
from api.models import CustomUser
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import base64
from django.contrib.auth import get_user_model

# Encrypt data
def encrypt_data(data, key):
    data_bytes = data.encode('utf-8')
    iv = os.urandom(16)  # Secure random IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

# Decrypt data
def decrypt_data(encrypted_data, key):
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    iv = encrypted_data_bytes[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data_bytes[16:]) + decryptor.finalize()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data.decode('utf-8')

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
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        mobile_number = request.data.get("mobile_number", None)

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if CustomUser.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mobile_number=mobile_number,
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "User registered successfully.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


User = get_user_model()

def custom_authenticate(email, password):
    try:
        user = User.objects.get(email__iexact=email)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        pass
    return None

# User Login
class Login(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(email=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        update_last_login(None, user)
        refresh = RefreshToken.for_user(user)
        user_data = CustomUserSerializer(user).data

        return Response(
            {
                "token": str(refresh.access_token),
                "user_data": user_data,
            },
            status=status.HTTP_200_OK,
        )

# Get Authenticated User Details
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def UserDetails(request):
    user = request.user
    user_data = CustomUserSerializer(user).data
    return Response({"user_data": user_data}, status=status.HTTP_200_OK)
