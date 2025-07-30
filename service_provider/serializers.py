from rest_framework import serializers

from accounts.models import User
from service_provider.models import TokenTransaction, CompanyProfile
from jobs.models import Job, SubCategory
import random
import string
from django.utils.crypto import get_random_string

def generate_password(length=10):
  return get_random_string(length)

def generate_otp():
  return ''.join(random.choices(string.digits, k=4))

