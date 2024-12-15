import os
import random
from django.utils import timezone
from twilio.rest import Client
from django.template.loader import render_to_string
from django.core.mail import send_mail
from api.models import OTP
from datetime import timedelta
from api.protos import otp_pb2_grpc, otp_pb2
from django.utils.timezone import now
from django.conf import settings

# Ensure that your Twilio credentials are securely retrieved from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "ACdff04487d1bc43ef8e5cc6ae114382fd")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "c0333460dbcf9be80d152c62ebcb4606")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+17753063489")  # Replace with your Twilio number

# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class OTPService(otp_pb2_grpc.OTPServiceServicer):
    def SendOTP(self, request, context):
        # Validate input
        mobile_number = request.mobile_number
        if not mobile_number:
            return otp_pb2.SendOTPResponse(success=False, message="Mobile number is required.")
        
        otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
        
        # Save OTP to the database with an expiry time of 5 minutes
        OTP.objects.create(
            mobile_number=mobile_number,
            otp=otp,
            expires_at=now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        )

        try:
            # Send the OTP via Twilio SMS
            client.messages.create(
                body=f"Your OTP is: {otp}",
                from_=TWILIO_PHONE_NUMBER,
                to=f"+91{mobile_number}",  # Assuming the mobile number is an Indian number
            )
            return otp_pb2.SendOTPResponse(success=True, message="OTP sent successfully.")
        except Exception as e:
            # Handle errors in sending OTP
            return otp_pb2.SendOTPResponse(success=False, message=f"Failed to send OTP: {str(e)}")

    def VerifyOTP(self, request, context):
        mobile_number = request.mobile_number
        otp = request.otp

        # Query the database for the OTP entry
        otp_entry = OTP.objects.filter(
            mobile_number=mobile_number,
            otp=otp,
            is_verified=False,
            expires_at__gt=now()
        ).first()

        if not otp_entry:
            return otp_pb2.VerifyOTPResponse(success=False, message="Invalid OTP or OTP has expired.")

        # Mark the OTP as verified
        otp_entry.is_verified = True
        otp_entry.save()

        return otp_pb2.VerifyOTPResponse(success=True, message="OTP verified successfully.")

# Send Access email for company owner
def send_access_email(user):
    try:
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
    except Exception as e:
        # Log the exception or handle appropriately
        print(f"Error sending access email: {str(e)}")

# Send welcome email for new user
def send_welcome_email(user):
    try:
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
    except Exception as e:
        # Log the exception or handle appropriately
        print(f"Error sending welcome email: {str(e)}")
