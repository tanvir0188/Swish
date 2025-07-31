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

class CompanyProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = CompanyProfile
    fields=['company_name', 'phone_number', 'ice_number', 'address', 'city', 'about','business_email','sub_category', 'facebook', 'instagram', 'youtube', 'tiktok', 'homepage', 'monday_time', 'tuesday_time','wednesday_time','thursday_time', 'friday_time', 'saturday_time','sunday_time', 'open_in_weekend']


