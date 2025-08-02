from collections import deque

from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Job, Area, SubCategory
from jobs.serializers import JobSerializer
from service_provider.filters import JobFilter
from service_provider.models import TokenPackage, TokenTransaction, CompanyProfile
from jobs.models import Job
from service_provider.serializers import CompanyProfileSerializer, JobListSerializer


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

class CompanyRegisterAPIView(APIView):
  permission_classes = [IsAuthenticated]
  @extend_schema(request=CompanyProfileSerializer, responses={
    200:'Ok', 400: 'Validation error'
  })
  def post(self, request):
    user = request.user
    try:
      company_profile = CompanyProfile.objects.get(user=user)

      return Response({
        'message': f'Already registered a company using {company_profile.user.email}.',
      }, status=status.HTTP_400_BAD_REQUEST)
    except CompanyProfile.DoesNotExist:
      serializer = CompanyProfileSerializer(data=request.data)
      try:
        if serializer.is_valid():
          serializer.save(user = user)
          return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
        return Response({
          'error': 'Something went wrong while registering the company.',
          'details': str(e)
        }, status=status.HTTP_502_BAD_GATEWAY)
@extend_schema(
  methods=["PATCH"],
  summary="Add work area to company profile",
  description="Adds a new area (if not existing) to the company’s profile and the global Area list.",
  request={
    "application/json": {
      "type": "object",
      "properties": {
        "area": {
          "type": "string",
          "example": "Casablanca"
        }
      },
      "required": ["area"]
    }
  },
  responses={
    200: OpenApiResponse(description="Area successfully added to company profile."),
    400: OpenApiResponse(description="Bad request – area missing."),
    403: OpenApiResponse(description="Forbidden – only company users can add areas.")
  }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def add_area(request):
  if request.user.role != 'company':
    return Response({"detail": "Only companies can add areas."}, status=status.HTTP_403_FORBIDDEN)

  area_name = request.data.get('area')
  if not area_name:
    return Response({"detail": "Area name is required."}, status=status.HTTP_400_BAD_REQUEST)

  # Get or create the Area object
  area_obj, created = Area.objects.get_or_create(name=area_name)

  # Add to the company profile
  company_profile = request.user.company_profile
  company_profile.area.add(area_obj)

  return Response({
    "detail": "Area added successfully.",
    "area": area_obj.name,
    "created_new": created
  }, status=status.HTTP_200_OK)

@extend_schema(
  methods=["PATCH"],
  summary="Add work type (sub-category) to company profile",
  description="Adds a new work type to the company’s profile. If it doesn’t exist globally, it is created.",
  request={
    "application/json": {
      "type": "object",
      "properties": {
        "work_type": {
          "type": "string",
          "example": "Electrician"
        }
      },
      "required": ["work_type"]
    }
  },
  responses={
    200: OpenApiResponse(description="Work type successfully added to company profile."),
    400: OpenApiResponse(description="Bad request – work_type missing."),
    403: OpenApiResponse(description="Forbidden – only company users can add work types.")
  }
)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def add_work_type(request):
  if request.user.role != 'company':
    return Response({"detail": "Only companies can add work types."}, status=status.HTTP_403_FORBIDDEN)

  work_type_name = request.data.get('work_type')
  if not work_type_name:
    return Response({"detail": "Work type is required."}, status=status.HTTP_400_BAD_REQUEST)

  # Get or create the SubCategory object
  subcategory_obj, created = SubCategory.objects.get_or_create(name=work_type_name)

  # Add to the company profile
  company_profile = request.user.company_profile
  company_profile.sub_category.add(subcategory_obj)

  return Response({
    "detail": "Work type added successfully.",
    "work_type": subcategory_obj.name,
    "created_new": created
  }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_job_list(request):
  user = request.user

  # Step 1: Get user's subcategories
  try:
    company_profile = user.company_profile
    subcategories = company_profile.sub_category.all()
  except:
    return Response({'error': 'No company profile or subcategories found'}, status=400)

  # Step 2: Filter jobs by subcategories (linked through Category)
  jobs = Job.objects.filter(
    category__in=[sub.category for sub in subcategories]
  ).exclude(
    posted_by=user  # ✅ Exclude jobs posted by the current user
  )

  # Step 3: Apply filters from query params
  job_filter = JobFilter(request.GET, queryset=jobs)

  # Step 4: Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(job_filter.qs, request)

  # Step 5: Serialize
  serializer = JobListSerializer(result_page, many=True)
  return paginator.get_paginated_response(serializer.data)

