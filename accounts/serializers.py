from rest_framework import serializers
from .models import User, Profile, PreSubscription
import re

class CreateUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'password', 'role', 'first_name', 'last_name', 'telephone', 'full_name', 'ice_number', 'company_name']
    extra_kwargs = {
      'password': {'write_only': True},
      'first_name': {'required': False, 'allow_null': True, 'allow_blank': True},
      'last_name': {'required': False, 'allow_null': True, 'allow_blank': True},
      'telephone': {'required': False, 'allow_null': True, 'allow_blank': True},
      'full_name': {'required': False, 'allow_null': True, 'allow_blank': True},
      'company_name': {'required': False, 'allow_null': True, 'allow_blank': True},
      'ice_number': {'required': False, 'allow_null': True, 'allow_blank': True},
    }

  def validate_password(self, password):
    if len(password) < 6:
      raise serializers.ValidationError("Password must be at least 6 characters long.")
    if not re.search(r'[A-Z]', password):
      raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
      raise serializers.ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):
      raise serializers.ValidationError("Password must contain at least one digit.")
    return password

  def validate_full_name(self, full_name):
    if full_name:
      if not re.match(r'^[A-Za-z ]+$', full_name):
        raise serializers.ValidationError("Full name can only contain letters and spaces.")
    return full_name

  def create(self, validated_data):
    password = validated_data.pop('password')
    user = User(**validated_data)
    user.set_password(password)
    user.save()
    return user


class OTPSerializer(serializers.Serializer):
  email = serializers.EmailField()
  otp = serializers.CharField(max_length=4)

class EmailSerializer(serializers.Serializer):
  email = serializers.EmailField()

class ResendOTPSerializer(serializers.Serializer):
  email = serializers.EmailField()

class OTPPasswordResetSerializer(serializers.Serializer):
  email = serializers.EmailField()
  otp = serializers.CharField(max_length=6)
  new_password = serializers.CharField(write_only=True, min_length=8)

class LogoutSerializer(serializers.Serializer):
  refresh_token = serializers.CharField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
  new_password = serializers.CharField(required=True)

class ProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = ['first_name', 'last_name', 'address', 'language', 'image']
    extra_kwargs = {
      ''
      'first_name': {'required': False, 'allow_blank': True},
      'last_name': {'required': False, 'allow_blank': True},
      'address': {'required': False, 'allow_blank': True},
      'language': {'required': False, 'allow_blank': True},
      'image': {'required': False},
    }

class SubscribeSerializer(serializers.ModelSerializer):
  class Meta:
    model = PreSubscription
    fields = ['email','role', 'phone_number', 'full_name', 'ice_number','company_name', 'city']
    extra_kwargs = {
      'telephone': {'required': False, 'allow_null': True, 'allow_blank': True},
      'full_name': {'required': False, 'allow_null': True, 'allow_blank': True},
      'company_name': {'required': False, 'allow_null': True, 'allow_blank': True},
      'ice_number': {'required': False, 'allow_null': True, 'allow_blank': True},
    }