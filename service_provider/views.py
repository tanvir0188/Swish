from collections import deque

from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Job
from service_provider.models import TokenPackage, TokenTransaction
from jobs.models import Job

class UnlockJobAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request, pk):
    used_by = request.user
    if used_by.role != 'company':
      return Response({
        'error': 'Unauthorized. You have to be a company to use tokens.'
      }, status=status.HTTP_403_FORBIDDEN)

    try:
      job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
      return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

    company = request.user

    try:
      # Get the earliest valid package
      package = TokenPackage.objects.filter(
        company=company,
        package_balance__gt=0,
        expires_at__gte=timezone.now()
      ).earliest('issued_at')
    except TokenPackage.DoesNotExist:
      return Response({'error': 'No available tokens'}, status=status.HTTP_400_BAD_REQUEST)

    try:
      # Create token transaction
      TokenTransaction.objects.create(
        package=package,
        job=job,
        used_by=used_by
      )
      package.package_balance -= 1
      package.save()

      return Response({
        'message': 'Job unlocked successfully',
        'token_balance': package.package_balance,
      }, status=status.HTTP_200_OK)

    except Exception as e:
      return Response({
        'error': 'Something went wrong while unlocking the job.',
        'details': str(e)
      }, status=status.HTTP_400_BAD_REQUEST)

class JobListApiView(APIView):
  permission_classes = [IsAuthenticated]
  def get(self, request):
    jobs = Job.objects.filter()
