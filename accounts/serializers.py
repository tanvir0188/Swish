from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, PreSubscription, ROLE_CHOICES, Feedback
import re

class CreateUserSerializer(serializers.ModelSerializer):
  role=serializers.ChoiceField(choices=ROLE_CHOICES)
  class Meta:
    model = User
    fields = ['email', 'password', 'role', 'first_name', 'surname', 'telephone']
    extra_kwargs = {
      'password': {'write_only': True},
      'first_name': {'required': False, 'allow_null': True, 'allow_blank': True},
      'surname': {'required': False, 'allow_null': True, 'allow_blank': True},
      'telephone': {'required': False, 'allow_null': True, 'allow_blank': True}
    }

  # def validate_password(self, password):
  #   if len(password) < 8:
  #     raise serializers.ValidationError("Password must be at least 6 characters long.")
  #   if not re.search(r'[A-Z]', password):
  #     raise serializers.ValidationError("Password must contain at least one uppercase letter.")
  #   if not re.search(r'[a-z]', password):
  #     raise serializers.ValidationError("Password must contain at least one lowercase letter.")
  #   if not re.search(r'\d', password):
  #     raise serializers.ValidationError("Password must contain at least one digit.")
  #   return password
  #
  # def validate_first_name(self, first_name):
  #   if first_name:
  #     if not re.match(r'^[A-Za-z ]+$', first_name):
  #       raise serializers.ValidationError("Full name can only contain letters and spaces.")
  #   return first_name
  # def validate_last_name(self, last_name):
  #   if last_name:
  #     if not re.match(r'^[A-Za-z ]+$', last_name):
  #       raise serializers.ValidationError("Full name can only contain letters and spaces.")
  #   return last_name

  def create(self, validated_data):
    password = validated_data.pop('password')
    user = User(**validated_data)
    user.set_password(password)
    user.save()
    return user

class ProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['first_name', 'surname', 'telephone', 'email', 'home_address', 'city']

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
  def validate_new_password(self, new_password):
    if len(new_password) < 8:
      raise serializers.ValidationError("Password must be at least 6 characters long.")
    if not re.search(r'[A-Z]', new_password):
      raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', new_password):
      raise serializers.ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', new_password):
      raise serializers.ValidationError("Password must contain at least one digit.")
    return new_password

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

class FeedbackSerializer(serializers.ModelSerializer):
  class Meta:
    model = Feedback
    fields=['suggestion']

class ChangeRoleSerializer(serializers.ModelSerializer):
  role = serializers.ChoiceField(choices=ROLE_CHOICES)
  class Meta:
    model = User
    fields = ['role']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
  @classmethod
  def get_token(cls, user):
    token = MyRefreshToken.for_user(user)
    return token

class MyRefreshToken(RefreshToken):
  @classmethod
  def for_user(cls, user):
    token = super().for_user(user)
    token['role'] = user.role
    return token