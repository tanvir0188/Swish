import random

from django.core.mail import send_mail
from .models import User
from swish import settings
def send_otp_for_password(email, otp):
  subject = "verification code for resetting password"
  message = f'Your verification code is {otp}. Expires in 1 minute.'
  email_from = settings.EMAIL_HOST
  send_mail(subject, message, email_from, [email])