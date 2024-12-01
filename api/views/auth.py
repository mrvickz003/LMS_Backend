from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from api.serializers import CustomUserSerializer
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import os
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

def encrypt_data(data, key):
    data_bytes = data.encode("utf-8")
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return (iv + encrypted_data).decode(
        "latin1"
    )  # Use 'latin1' to represent binary data in string format

class GetToken(APIView):
    def get(self, request):
        # Generate two random tokens
        random_tokens = [
            os.urandom(16).hex() for _ in range(2)
        ]  # Two 32-character random tokens
        print(random_tokens)
        # Define a 32-byte AES key
        key = b"092bec3416cef292e366a50b90b9f469"  # Replace with a secure key

        # Encrypt each token
        encrypted_tokens = [encrypt_data(token, key) for token in random_tokens]

        # Return the encrypted tokens in the specified format
        return Response(
            {
                "data": encrypted_tokens,
            },
            status=status.HTTP_200_OK,
        )

class Register(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        mobile_number = request.data.get("mobile_number", None)

        # Check for required fields
        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the user
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile_number,
            )

            # Generate JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "User registered successfully.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

class Login(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate input
        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(email=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Update the user's last login time
        update_last_login(None, user)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Serialize user data
        user_data = CustomUserSerializer(user).data

        # Return tokens and user data
        return Response(
            {
                "token": str(refresh.access_token),
                "user_data": user_data
            },
            status=status.HTTP_200_OK
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only authenticated users can access this view
def UserDetails(request):
    try:
        # Use the authenticated user's details
        user = request.user

        # Serialize the user data
        user_data = CustomUserSerializer(user).data
        
        return Response({"user_data": user_data}, status=200)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)