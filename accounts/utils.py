import random

from django.core.mail import send_mail
from swish import settings
from django.utils import timezone
from datetime import timedelta
from .models import User  # or use get_user_model()

def send_otp_for_password(email, otp):
  subject = "Verification Code for Resetting Password"
  plain_message = f'Your verification code is {otp}. Expires in 3 minute.'
  html_message = f'''
    <html>
      <body>
        <p>Your verification code is <strong style="color: green;">{otp}</strong>.</p>
        <p>Expires in 1 minute.</p>
      </body>
    </html>
  '''
  email_from = settings.EMAIL_HOST_USER  # should be EMAIL_HOST_USER, not EMAIL_HOST
  send_mail(subject, plain_message, email_from, [email], html_message=html_message)

def send_otp_for_email_verification(email, otp):
  subject = "Verification Code for Email registration"
  plain_message = f'Your verification code is {otp}. Expires in 1 minute.'
  html_message = f'''
    <html>
      <body>
        <p>Your verification code is <strong style="color: green;">{otp}</strong>.</p>
        <p>Expires in 1 minute.</p>
      </body>
    </html>
  '''
  email_from = settings.EMAIL_HOST_USER
  send_mail(subject, plain_message, email_from, [email], html_message=html_message)