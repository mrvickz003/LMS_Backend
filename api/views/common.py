from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import base64
from django.conf import settings
from twilio.rest import Client
from django.template.loader import render_to_string
from django.core.mail import send_mail

# API to get a secure random token
class GetToken(APIView):
    def get(self, request):
        key = os.urandom(32)
        random_token = os.urandom(16).hex()
        encrypted_token = encrypt_data(random_token, key)
        return Response({"token": encrypted_token}, status=status.HTTP_200_OK)

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

# Send realtime mobile otp 

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
# Send mobile otp for terminal
def send_otp(mobile_number, otp):
        print(f"Sending OTP {otp} to {mobile_number}")
        return True
"""
# Send Access mail for company owner 
def send_access_email(user):
    subject = "Access Granted"
    html_message = render_to_string(
        'send_access_email.html', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'current_year': timezone.now().year,
        }
    )
    from_email = "no-reply@example.com"
    recipient_list = [user.email]
    send_mail(subject, "", from_email, recipient_list, html_message=html_message)

# Send welcome mail for new user 
def send_welcome_email(user):
    subject = "Welcome to LMS"
    html_message = render_to_string(
        'welcome_mail.html', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'current_year': timezone.now().year,
        }
    )
    from_email = "no-reply@example.com"
    recipient_list = [user.email]
    send_mail(subject, "", from_email, recipient_list, html_message=html_message)