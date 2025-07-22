from rest_framework import serializers
from .models import User, Profile

class CreateUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'first_name', 'last_name', 'telephone', 'password']
    extra_kwargs = {'password': {'write_only': True}}

  def create(self, validated_data):
    user = User(
      email=validated_data['email'],
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name'],
      telephone=validated_data['telephone'],
    )
    user.set_password(validated_data['password'])
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