import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.http import JsonResponse
from api.serializers import CustomUserSerializer
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import os
from rest_framework.permissions import AllowAny



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
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                return Response(
                    {"error": "Email and password are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Custom authentication
            user = custom_authenticate(email=email, password=password)
            if user is None:
                self.log_failed_attempt(email)
                return Response(
                    {"error": "Invalid email or password."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            user_data = CustomUserSerializer(user).data
            
            return Response(
                {"token": str(refresh.access_token), "user_data": user_data},
                status=status.HTTP_200_OK,
            )

        except UnicodeDecodeError as e:
            # Return a more helpful error message
            return JsonResponse(
                {"error": f"Encoding error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def log_failed_attempt(email):
        print(f"Failed login attempt for email: {email} at {now()}")
