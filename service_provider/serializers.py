from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from accounts.models import User
from service_provider.models import TokenTransaction, CompanyProfile, Bid, TokenPackage
from jobs.models import Job, SubCategory, Favorite, Area
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

class AddFavoriteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Favorite
    fields = ['job']

class SubCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = SubCategory
    fields = ['id', 'name']

class AreaSerializer(serializers.ModelSerializer):
  number_of_jobs=serializers.SerializerMethodField()
  class Meta:
    model = Area
    fields = ['id', 'name', 'number_of_jobs']

  def get_number_of_jobs(self, obj):
    return Job.objects.filter(area=obj).count()

class SideBarInfoSerializer(serializers.ModelSerializer):
  sub_category = SubCategorySerializer(many=True, read_only=True)
  area = AreaSerializer(many=True, read_only=True)
  tokens = serializers.SerializerMethodField()

  class Meta:
    model = CompanyProfile  # Replace with your actual model name
    fields = ['sub_category', 'area', 'tokens']

  def get_tokens(self, obj):
    user = obj.user  # Assuming CompanyProfile has a FK to User named `user`
    valid_tokens = TokenPackage.objects.filter(
      company=user,
      package_balance__gt=0,
      expires_at__gt=timezone.now()
    ).aggregate(total=Sum('package_balance'))['total'] or 0
    return valid_tokens



class JobListSerializer(serializers.ModelSerializer):
  posted_by = serializers.SerializerMethodField()
  image = serializers.SerializerMethodField()
  description = serializers.SerializerMethodField()
  bids = serializers.SerializerMethodField()
  is_favorite=serializers.SerializerMethodField()

  class Meta:
    model = Job
    fields = ['id', 'posted_by', 'image', 'heading','value', 'mission_address', 'created_at', 'description', 'bids', 'is_favorite']

  def get_posted_by(self, obj):
    return f"{obj.first_name} {obj.surname}"

  def get_image(self, obj):
    user_image = getattr(obj.posted_by, 'image', None)
    return user_image.url if user_image else "https://png.pngtree.com/png-vector/20220608/ourmid/pngtree-unnamed-user-avatar-icon-profile-png-image_4816337.png"

  def get_description(self, obj):
    return obj.description[:len(obj.description) // 5] + '...'  # 20%

  def get_bids(self, obj):
    return Bid.objects.filter(job=obj).count()

  def get_is_favorite(self, obj):
    request = self.context.get('request')
    user = request.user if request else None

    if user and user.is_authenticated:
      return Favorite.objects.filter(user=user.id, job=obj).exists()
    return False


