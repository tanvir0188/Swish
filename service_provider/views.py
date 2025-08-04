from collections import deque
from django.db.models.aggregates import Sum
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from jobs.models import Job, Area, SubCategory, Favorite
from jobs.serializers import JobSerializer, SubCategorySerializer
from service_provider.filters import JobFilter
from service_provider.models import TokenPackage, TokenTransaction, CompanyProfile, Bid
from jobs.models import Job
from service_provider.serializers import CompanyProfileSerializer, JobListSerializer, AddFavoriteSerializer, \
  BiddingSerializer


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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Job
from .serializers import JobDescriptionSerializer

class JobDetailAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request, pk):
    try:
      job = Job.objects.get(pk=pk)
      serializer = JobDescriptionSerializer(job, context={'request': request})
      if not serializer.data.get('is_unlocked'):
        return Response({
          'error': 'You have to unlock the job first',
        }, status=status.HTTP_403_FORBIDDEN)
      return Response(serializer.data, status=status.HTTP_200_OK)
    except Job.DoesNotExist:
      return Response({'detail': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyRegisterAPIView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request=CompanyProfileSerializer,
    responses={200: CompanyProfileSerializer, 400: 'Validation error'}
  )
  def post(self, request):
    user = request.user
    if hasattr(user, 'company_profile'):
      return Response({
        'message': f'Already registered a company using {user.email}.',
      }, status=status.HTTP_400_BAD_REQUEST)

    serializer = CompanyProfileSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(user=user)
      return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @extend_schema(
    request=CompanyProfileSerializer,
    responses={200: CompanyProfileSerializer, 404: 'Not found', 400: 'Validation error'}
  )
  def patch(self, request):
    user = request.user
    try:
      company_profile = user.company_profile
    except CompanyProfile.DoesNotExist:
      return Response({'error': 'Company profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompanyProfileSerializer(company_profile, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @extend_schema(
    responses={200: CompanyProfileSerializer, 404: 'Not found'}
  )
  def get(self, request):
    user = request.user
    try:
      company_profile = user.company_profile
      serializer = CompanyProfileSerializer(company_profile)
      return Response(serializer.data, status=status.HTTP_200_OK)
    except CompanyProfile.DoesNotExist:
      return Response({'error': 'Company profile not found.'}, status=status.HTTP_404_NOT_FOUND)

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

class ToggleFavoriteAPIView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request=AddFavoriteSerializer,
    responses={200: 'Ok', 400: 'Validation error'}
  )
  def post(self, request):
    if request.user.role != 'company':
      return Response({
        "message": "Only companies can manage favorites."
      }, status=status.HTTP_403_FORBIDDEN)

    serializer = AddFavoriteSerializer(data=request.data)
    if serializer.is_valid():
      job = serializer.validated_data['job']
      user = request.user

      # Try to get existing favorite entry
      favorite = Favorite.objects.filter(user=user, job=job).first()
      if favorite:
        favorite.delete()
        return Response({'message': 'Removed from favorites'}, status=status.HTTP_200_OK)
      else:
        Favorite.objects.create(user=user, job=job)
        return Response({'message': 'Added to favorites'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
  parameters=[
    OpenApiParameter(name='min_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Minimum job value'),
    OpenApiParameter(name='max_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Maximum job value'),
    OpenApiParameter(name='subcategory', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by subcategory name'),
    OpenApiParameter(name='area', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by area name'),
    OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Search by Job heading'),
    OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Page number for pagination')
  ],
  responses=JobListSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_all_job_list(request):
  # Filter jobs in relevant subcategories and exclude self-posted
  if request.user.role != 'company':
    return Response({'message':'Change your role to Company'},status=status.HTTP_403_FORBIDDEN)
  jobs = Job.objects.all()
  # Apply JobFilter
  job_filter = JobFilter(request.GET, queryset=jobs)

  # Apply distinct here to avoid duplicates from joins
  filtered_jobs = job_filter.qs.distinct().order_by('-created_at')
  # Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(filtered_jobs, request)
  # Serialize
  serializer = JobListSerializer(result_page, many=True, context={'request': request})
  return paginator.get_paginated_response(serializer.data)

@extend_schema(
  parameters=[
    OpenApiParameter(name='min_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Minimum job value'),
    OpenApiParameter(name='max_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Maximum job value'),
    OpenApiParameter(name='subcategory', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by subcategory name'),
    OpenApiParameter(name='area', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by area name'),
    OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Search by Job heading'),
    OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Page number for pagination')
  ],
  responses=JobListSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_recommended_job_list(request):
  user = request.user
  if user.role != 'company':
    return Response({'message':'Change your role to Company'},status=status.HTTP_403_FORBIDDEN)
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
  filtered_jobs = job_filter.qs.distinct().order_by('-created_at')

  # Step 4: Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(filtered_jobs, request)

  # Step 5: Serialize
  serializer = JobListSerializer(result_page, many=True, context={'request': request})
  return paginator.get_paginated_response(serializer.data)



@extend_schema(
  parameters=[
    OpenApiParameter(name='min_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Minimum job value'),
    OpenApiParameter(name='max_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Maximum job value'),
    OpenApiParameter(name='subcategory', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by subcategory name'),
    OpenApiParameter(name='area', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by area name'),
    OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Search by Job heading'),
    OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Page number for pagination')
  ],
  responses=JobListSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_new_job_list(request):
  user = request.user
  if user.role != 'company':
    return Response({'message':'Change your role to Company'},status=status.HTTP_403_FORBIDDEN)

  try:
    company_profile = user.company_profile
    subcategories = company_profile.sub_category.all()
  except:
    return Response({'error': 'No company profile or subcategories found'}, status=400)

  # Filter jobs in relevant subcategories and exclude self-posted
  jobs = Job.objects.filter(
    category__in=[sub.category for sub in subcategories]
  ).exclude(
    posted_by=user
  )

  # Exclude jobs already unlocked
  unlocked_job_ids = TokenTransaction.objects.filter(used_by=user).values_list('job_id', flat=True)
  jobs = jobs.exclude(id__in=unlocked_job_ids)

  # Apply JobFilter
  job_filter = JobFilter(request.GET, queryset=jobs)

  # Apply distinct here to avoid duplicates from joins
  filtered_jobs = job_filter.qs.distinct().order_by('-created_at')

  # Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(filtered_jobs, request)

  # Serialize
  serializer = JobListSerializer(result_page, many=True, context={'request': request})
  return paginator.get_paginated_response(serializer.data)

@extend_schema(
  parameters=[
    OpenApiParameter(name='min_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Minimum job value'),
    OpenApiParameter(name='max_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Maximum job value'),
    OpenApiParameter(name='subcategory', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by subcategory name'),
    OpenApiParameter(name='area', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by area name'),
    OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Search by Job heading'),
    OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Page number for pagination')
  ],
  responses=JobListSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_favorite_job_list(request):
  user = request.user
  if user.role != 'company':
    return Response({'message':'Change your role to Company'},status=status.HTTP_403_FORBIDDEN)
  try:
    company_profile = user.company_profile
    subcategories = company_profile.sub_category.all()
  except:
    return Response({'error': 'No company profile or subcategories found'}, status=400)

  # Filter jobs in relevant subcategories and exclude self-posted
  jobs = Job.objects.filter(
    category__in=[sub.category for sub in subcategories]
  ).exclude(
    posted_by=user
  )

  # Include only favorited jobs (not exclude)
  favorite_job_ids = Favorite.objects.filter(user=user).values_list('job_id', flat=True)
  jobs = jobs.filter(id__in=favorite_job_ids)

  # Apply JobFilter
  job_filter = JobFilter(request.GET, queryset=jobs)

  # Apply distinct here to avoid duplicates from joins
  filtered_jobs = job_filter.qs.distinct()

  # Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(filtered_jobs, request)

  # Serialize
  serializer = JobListSerializer(result_page, many=True, context={'request': request})
  return paginator.get_paginated_response(serializer.data)

@extend_schema(
  parameters=[
    OpenApiParameter(name='min_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Minimum job value'),
    OpenApiParameter(name='max_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Maximum job value'),
    OpenApiParameter(name='subcategory', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by subcategory name'),
    OpenApiParameter(name='area', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by area name'),
    OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Search by Job heading'),
    OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Page number for pagination')
  ],
  responses=JobListSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_responded_job_list(request):
  user = request.user
  if user.role != 'company':
    return Response({'message':'Change your role to Company'},status=status.HTTP_403_FORBIDDEN)

  try:
    company_profile = user.company_profile
    subcategories = company_profile.sub_category.all()
  except:
    return Response({'error': 'No company profile or subcategories found'}, status=400)

  # Get jobs unlocked by the user via TokenTransaction
  unlocked_job_ids = TokenTransaction.objects.filter(used_by=user).values_list('job_id', flat=True)

  jobs = Job.objects.filter(
    id__in=unlocked_job_ids,
    category__in=[sub.category for sub in subcategories]
  ).exclude(
    posted_by=user
  )

  # Apply filtering
  job_filter = JobFilter(request.GET, queryset=jobs)
  filtered_jobs = job_filter.qs.distinct()

  # Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(filtered_jobs, request)

  serializer = JobListSerializer(result_page, many=True, context={'request': request})
  return paginator.get_paginated_response(serializer.data)


@extend_schema(
  parameters=[
    OpenApiParameter(name='min_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Minimum job value'),
    OpenApiParameter(name='max_value', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Maximum job value'),
    OpenApiParameter(name='subcategory', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by subcategory name'),
    OpenApiParameter(name='area', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Filter by area name'),
    OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Search by Job heading'),
    OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Page number for pagination')
  ],
  responses=JobListSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_won_job_list(request):
  user = request.user
  if user.role != 'company':
    return Response({'message':'Change your role to Company'},status=status.HTTP_403_FORBIDDEN)

  try:
    company_profile = user.company_profile
    subcategories = company_profile.sub_category.all()
  except:
    return Response({'error': 'No company profile or subcategories found'}, status=400)

  # Get jobs where user has bidded with status 'Complete'
  won_job_ids = Bid.objects.filter(
    bidding_company=user,
    status='Complete',
    job__category__in=[sub.category for sub in subcategories]
  ).values_list('job_id', flat=True)

  jobs = Job.objects.filter(
    id__in=won_job_ids
  ).exclude(
    posted_by=user
  )

  # Apply filtering
  job_filter = JobFilter(request.GET, queryset=jobs)
  filtered_jobs = job_filter.qs.distinct()

  # Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(filtered_jobs, request)

  serializer = JobListSerializer(result_page, many=True, context={'request': request})
  return paginator.get_paginated_response(serializer.data)

class SideBarInfoAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    user = request.user

    # Check company profile existence
    company_profile = getattr(user, 'company_profile', None)
    if not company_profile:
      return Response({
        "error": "User does not have a company profile."
      }, status=400)

    # Get all subcategories
    sub_categories = list(SubCategory.objects.values_list('name', flat=True))

    # Get all areas with job count
    areas = []
    for area in Area.objects.all():
      job_count = Job.objects.filter(area=area).count()

      areas.append(
        f"{area.name} ({job_count})"
      )

    # Get total valid tokens
    valid_tokens = TokenPackage.objects.filter(
      company=user,
      package_balance__gt=0,
      expires_at__gt=timezone.now()
    ).aggregate(total=Sum('package_balance'))['total'] or 0

    # Construct and return response
    return Response({
      'sub_categories': sub_categories,
      'areas': areas,
      'tokens': valid_tokens
    })

class CompanyBiddingAPIView(APIView):
  permission_classes = [IsAuthenticated]
  @extend_schema(
    request=BiddingSerializer,
    responses=BiddingSerializer
  )
  def post(self, request, pk):
    bidding_company = request.user
    job =Job.objects.get(pk=pk)
    if Bid.objects.filter(bidding_company=bidding_company, job=job).exists():
      return Response({
        "error": "You already have bid for this job."
      }, status=400)
    serializer = BiddingSerializer(data=request.data)
    is_unlocked = TokenTransaction.objects.filter(job=job, used_by=bidding_company).exists()

    if serializer.is_valid():
      if not is_unlocked:
        return Response({'message': "You have not unlocked this job yet"}, status=status.HTTP_403_FORBIDDEN)
      serializer.save(job=job, bidding_company=bidding_company)
      return Response({
        "data":serializer.data,
        "message": f"Bid submitted for '{job.heading}'"
      }, status=status.HTTP_201_CREATED)
    return Response({
      "error": serializer.errors,
      "message": 'Something went wrong.',
    }, status=status.HTTP_400_BAD_REQUEST)

  @extend_schema(
    request=BiddingSerializer,
    responses=BiddingSerializer
  )
  def patch(self, request, pk):
    bidding_company = request.user
    try:
      job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
      return Response({"error": "Job not found."}, status=404)

    try:
      bid = Bid.objects.get(job=job, bidding_company=bidding_company)
    except Bid.DoesNotExist:
      return Response({"error": "You don't have a bid for this job."}, status=404)

    serializer = BiddingSerializer(bid, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response({
        "data": {
          "time_estimate": serializer.data['time_estimate'],
          "proposal_description": serializer.data['proposal_description'],
          "price": serializer.data['price']

        },
        "message": f"Updated the bid for {job.heading}"
      }, status=status.HTTP_200_OK)

    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





