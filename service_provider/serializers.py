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

class JobListSerializer(serializers.ModelSerializer):
  posted_by = serializers.SerializerMethodField()
  image = serializers.SerializerMethodField()
  description = serializers.SerializerMethodField()
  bids = serializers.SerializerMethodField()
  is_favorite=serializers.SerializerMethodField()
  is_unlocked= serializers.SerializerMethodField()
  bid_status = serializers.SerializerMethodField()

  class Meta:
    model = Job
    fields = ['id', 'posted_by', 'image', 'heading','value', 'mission_address', 'created_at', 'description', 'bids', 'is_favorite', 'is_unlocked', 'bid_status']

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

  def get_is_unlocked(self, obj):
    request = self.context.get('request')
    user = request.user if request else None

    if user and user.is_authenticated:
      return TokenTransaction.objects.filter(job=obj, used_by=user).exists()
    return False
  def get_bid_status(self, obj):
    request = self.context.get('request')
    user = request.user if request else None
    if user and user.is_authenticated:
      return Bid.objects.filter(job=obj, bidding_company=user).exists()
    return False

class JobDescriptionSerializer(serializers.ModelSerializer):
  project_value=serializers.SerializerMethodField()
  contact= serializers.SerializerMethodField()
  property_type= serializers.SerializerMethodField()
  property_pictures=serializers.SerializerMethodField()
  scale = serializers.SerializerMethodField()
  is_unlocked=serializers.SerializerMethodField()
  is_favorite=serializers.SerializerMethodField()
  class Meta:
    model = Job
    fields = ['posted_by', 'heading', 'description', 'created_at', 'project_value', 'mission_address', 'employee_need','contact', 'property_type', 'scale', 'property_pictures', 'is_favorite', 'is_unlocked']

  def get_contact(self, obj):
    return obj.telephone
  def get_property_type(self, obj):
    return obj.category.name

  def get_is_favorite(self, obj):
    request = self.context.get('request')
    user = request.user if request else None

    if user and user.is_authenticated:
      return Favorite.objects.filter(user=user.id, job=obj).exists()
    return False

  def get_project_value(self, obj):
    return obj.value

  def get_contact(self, obj):
    return obj.telephone_number
  def get_scale(self, obj):
    return obj.scale
  def get_property_pictures(self, obj):
    request = self.context.get('request')
    return [
      request.build_absolute_uri(image.image.url)
      for image in obj.images.all()
    ]

  def get_is_unlocked(self, obj):
    request = self.context.get('request')
    user = request.user if request else None

    if user and user.is_authenticated:
      return TokenTransaction.objects.filter(job=obj, used_by=user).exists()
    return False

class BiddingSerializer(serializers.ModelSerializer):
  price = serializers.FloatField(write_only=True)
  job = serializers.Serializer(read_only=True)
  bidding_company = serializers.Serializer(read_only=True)

  class Meta:
    model = Bid
    fields = ['job', 'bidding_company', 'price', 'time_estimate', 'proposal_description']

  def create(self, validated_data):
    price = validated_data.pop('price')
    validated_data['amount'] = price
    return super().create(validated_data)

  def update(self, instance, validated_data):
    price = validated_data.pop('price', None)
    if price is not None:
      instance.amount = price
    return super().update(instance, validated_data)

  def to_representation(self, instance):
    data = super().to_representation(instance)
    data['price'] = instance.amount
    return data

