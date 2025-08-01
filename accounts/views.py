from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from rest_framework import status
import random

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from jobs.serializers import SubCategorySerializer
from .models import User
from .serializers import CreateUserSerializer, LogoutSerializer, OTPSerializer, EmailSerializer, \
  ChangePasswordSerializer, SubscribeSerializer, FeedbackSerializer, ProfileSerializer, ChangeRoleSerializer, \
  MyTokenObtainPairSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone

from .utils import send_otp_for_password


class RegisterView(APIView):
  @extend_schema(
    request=CreateUserSerializer,
    responses={201: 'User registered successfully', 400: 'Validation error'}
  )
  def post(self, request):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
      user = serializer.save()
      response_data = {
        'message': 'User registered successfully',
        'user': {
          'id': user.id,
          'email': user.email,
          'role': user.role,
          'first_name': user.first_name,
          'surname': user.surname,
          'telephone': user.telephone,
        }
      }
      return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ProfileView(APIView):
  permission_classes = [IsAuthenticated]
  @extend_schema(
    request=ProfileSerializer,
    responses={200: 'User profile successfully updated', 400: 'Validation error'}
  )
  def patch(self, request):
    user = request.user
    serializer = ProfileSerializer(user,data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
  request=EmailSerializer,
  responses={200: None, 400: 'Validation error'}
)
class SubscribeView(APIView):
  @extend_schema(
    request=SubscribeSerializer,
    responses={200: None, 400: 'Validation error'}
  )
  def post(self, request):
    serializer = SubscribeSerializer(data=request.data)
    if serializer.is_valid():
      try:
        serializer.save()
        return Response({"message": "Subscription successful"}, status=status.HTTP_200_OK)
      except Exception as e:
        return Response(
          {"error": "An error occurred while saving data.", "details": str(e)},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
  request=EmailSerializer,
  responses={200: None, 400: 'Validation error'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def forget_password_otp(request):
  serializer = EmailSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=400)

  email = serializer.validated_data['email']

  try:
    user = User.objects.get(email=email)
  except User.DoesNotExist:
    return Response({'error': 'User not found'}, status=404)

  otp = random.randint(1000, 9999)
  user.otp = otp
  user.otp_expires = timezone.now() + timedelta(minutes=1)
  user.save()

  send_otp_for_password(user.email, otp)

  return Response({
    'message': 'OTP sent successfully.',
    'status': 'success'
  }, status=200)

class VerifyOTPView(APIView):
  @extend_schema(
    request=OTPSerializer,
    responses={
      200: OpenApiResponse(description='OTP verified successfully with tokens'),
      400: OpenApiResponse(description='Invalid or expired OTP'),
      404: OpenApiResponse(description='User not found'),
    }
  )
  def patch(self, request):
    serializer = OTPSerializer(data=request.data)
    if serializer.is_valid():
      email = serializer.validated_data['email']
      otp = serializer.validated_data['otp']

      try:
        user = User.objects.get(email=email)
      except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

      if user.otp != otp:

        return Response({'error': 'Invalid OTP'}, status=400)


      if user.otp_expires < timezone.now():

        return Response({'error': 'OTP expired'}, status=400)
      user.otp = None
      user.otp_expires = None
      user.save()

      refresh = RefreshToken.for_user(user)
      return Response({
        'message': 'OTP verified successfully.',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
      }, status=200)

    return Response(serializer.errors, status=400)

class LogoutAPIView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request=LogoutSerializer,
    responses={205: None, 400: 'Validation Error'}
  )
  def post(self, request):
    serializer = LogoutSerializer(data=request.data)
    if serializer.is_valid():
      refresh_token = serializer.validated_data['refresh_token']
      try:
        RefreshToken(refresh_token).blacklist()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
      except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordAPIView(APIView):
  permission_classes = [IsAuthenticated]


  @extend_schema(
    request=ChangePasswordSerializer,
    responses={200:None, 400: 'Validation Error'}
  )
  def patch(self, request):
    user = request.user
    serializer = ChangePasswordSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    new_password = serializer.validated_data['new_password']

    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password changed successfully.'}, status=200)

class FeedbackAPIView(APIView):
  permission_classes = [IsAuthenticated]
  @extend_schema(
    request=FeedbackSerializer,
    responses={200: None, 400: 'Validation Error'}
  )
  def post(self, request):
    serializer = FeedbackSerializer(data=request.data)
    try:
      if serializer.is_valid():
        serializer.save(user=request.user)
        return Response('Feedback posted successfully', status=200)
      return Response(serializer.errors, status=400)
    except Exception as e:
      return Response({'error': str(e)}, status=400)

class ChangeRoleApiView(APIView):
  permission_classes = [IsAuthenticated]
  @extend_schema(
    request=ChangeRoleSerializer,
    responses={200: None, 400: 'Validation Error'}
  )
  def patch(self, request):
    user = request.user
    serializer = ChangeRoleSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
      serializer.save()
      return Response({'message': f'Role updated to {user.role}'}, status=200)

    return Response(serializer.errors, status=400)

class MyTokenObtainPairView(TokenObtainPairView):
  serializer_class = MyTokenObtainPairSerializer



