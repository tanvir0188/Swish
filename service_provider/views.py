from collections import deque, defaultdict
from django.db.models.aggregates import Sum
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from jobs.models import Job, Area, SubCategory, Favorite
from jobs.serializers import ReviewSerializer
from service_provider.filters import JobFilter
from service_provider.models import TokenPackage, TokenTransaction, CompanyProfile, Bid, Employee
from service_provider.serializers import CompanyProfileSerializer, JobListSerializer, AddFavoriteSerializer, \
  BiddingSerializer, CompanyProfileDetailSerializer, SubCategorySerializer, CompanyLogoWallpaperSerializer, \
  EmployeeListSerializer, EmployeeSerializer


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

class EditSubCategoryAPIView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request={
      "application/json": {
        "type": "object",
        "properties": {
          "sub_category": {
            "type": "array",
            "items": {
              "type": "integer"
            },
            "description": "List of SubCategory IDs"
          }
        },
        "example": {
          "sub_category": [2, 5, 9]
        }
      }
    },
    responses={
      200: OpenApiTypes.OBJECT,
      400: OpenApiTypes.OBJECT,
      404: OpenApiTypes.OBJECT
    },
    description="Patch company profile's sub_category field by sending a list of SubCategory IDs."
  )

  def patch(self, request):
    try:
      company_profile = request.user.company_profile
    except CompanyProfile.DoesNotExist:
      return Response({'error': 'Company profile not found'}, status=status.HTTP_404_NOT_FOUND)

    subcategory_ids = request.data.get('sub_category')

    if not isinstance(subcategory_ids, list):
      return Response({'error': 'sub_category must be a list of IDs'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate SubCategory IDs
    valid_subcategories = SubCategory.objects.filter(id__in=subcategory_ids)
    if valid_subcategories.count() != len(subcategory_ids):
      return Response({'error': 'Some SubCategory IDs are invalid'}, status=status.HTTP_400_BAD_REQUEST)

    # Update sub_category field
    company_profile.sub_category.set(valid_subcategories)
    company_profile.save()

    return Response({'message': 'Sub categories updated successfully'}, status=status.HTTP_200_OK)

class CompanyProfileAPIView(APIView):
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

class CompanyProfileDetailAPIView(APIView):
  permission_classes = [IsAuthenticated]
  def get(self, request):
    user = request.user
    if user.role =='private':
      return Response({'error':'Change your role to Company first'}, status=status.HTTP_403_FORBIDDEN)
    company_profile=user.company_profile
    serializer = CompanyProfileDetailSerializer(company_profile)
    try:
      return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_company_cat_and_sub_cat(request):
  company_profile = request.user.company_profile
  sub_categories = company_profile.sub_category.select_related('category').all()

  # Group subcategories by their category
  grouped_data = defaultdict(list)
  for sub in sub_categories:
    grouped_data[sub.category.name].append(sub)

  # Format the response
  result = []
  for category_name, subs in grouped_data.items():
    result.append({
      "category_name": category_name,
      "sub_categories": SubCategorySerializer(subs, many=True).data
    })

  return Response({'data': result}, status=status.HTTP_200_OK)

class CompanyLogoAndWallpaperAPIView(APIView):
  permission_classes = [IsAuthenticated]
  def get(self, request):
    try:
      company_profile = request.user.company_profile
      serializer = CompanyLogoWallpaperSerializer(company_profile)
      return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  def patch(self, request):
    try:
      if request.user.role!='company':
        return Response({
          'error':'Change your role to Company first',
        })
      company_profile = request.user.company_profile
      serializer = CompanyLogoWallpaperSerializer(company_profile, data=request.data, partial=True)
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
  methods=["PATCH"],
    request={
      "application/json": {
        "type": "object",
        "properties": {
          "company_name": {
            "type": "string",
            "example": "string"
          },
          "email": {
            "type": "string",
            "example": "user@example.com"
          },
          "telephone": {
            "type": "string",
            "example": "string"
          },
          "location": {
            "type": "string",
            "example": "example"
          }
        }
      }
    },
    responses={
    200: OpenApiResponse(description="Profile updated successfully")

  }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@extend_schema()
def patch_company_profile(request):
  user = request.user
  if user.role == 'company':
    company_profile = user.company_profile
    company_name = request.data.get('company_name')
    email = request.data.get('email')
    telephone = request.data.get('telephone')
    location = request.data.get('location')
    try:
      company_profile.company_name = company_name
      company_profile.business_email = email
      company_profile.phone_number = telephone
      company_profile.address = location
      company_profile.save()
      return Response({
        'message': 'Company profile updated successfully',
        'data':{
          'company_name': company_name,
          'email': email,
          'telephone': telephone,
          'location': location,
        }
      }, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  return Response({
    'error': 'Change your role to company first',
  }, status=status.HTTP_403_FORBIDDEN)


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
    OpenApiParameter(name='source', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Source: favorite, responded, won, new, or recommended'),
    OpenApiParameter(name='size', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Comma-separated sizes (e.g., small,medium)'),
    OpenApiParameter(name='subcategory', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Comma-separated subcategory names'),
    OpenApiParameter(name='area', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Comma-separated area names'),
    OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Search by Job heading'),
    OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Page number for pagination')
  ],
  responses=JobListSerializer(many=True)
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filtered_job_list(request):
  user = request.user
  source = request.GET.get('source')

  if user.role != 'company':
    return Response({'message': 'Change your role to Company'}, status=status.HTTP_403_FORBIDDEN)

  jobs = Job.objects.none()  # default empty queryset

  if source == 'all':
    jobs = Job.objects.all()

  elif source == 'favorite':
    favorite_job_ids = Favorite.objects.filter(user=user).values_list('job_id', flat=True)
    jobs = Job.objects.filter(id__in=favorite_job_ids)

  elif source == 'responded':
    unlocked_job_ids = TokenTransaction.objects.filter(used_by=user).values_list('job_id', flat=True)
    jobs = Job.objects.filter(id__in=unlocked_job_ids)

  elif source == 'won':
    won_job_ids = Bid.objects.filter(
      bidding_company=user,
      status='Complete'
    ).values_list('job_id', flat=True)
    jobs = Job.objects.filter(id__in=won_job_ids).exclude(posted_by=user)

  elif source == 'new':
    unlocked_job_ids = TokenTransaction.objects.filter(used_by=user).values_list('job_id', flat=True)
    jobs = Job.objects.exclude(posted_by=user).exclude(id__in=unlocked_job_ids)


  elif source == 'recommended':

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

  # Apply filters only if jobs queryset is not empty
  if jobs.exists():
    job_filter = JobFilter(request.GET, queryset=jobs)
    filtered_jobs = job_filter.qs.distinct()
  else:
    filtered_jobs = jobs

  # Paginate
  paginator = PageNumberPagination()
  paginator.page_size = 6
  result_page = paginator.paginate_queryset(filtered_jobs, request)

  # Serialize
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

class EmployeeApiView(APIView):
  permission_classes = [IsAuthenticated]
  def get(self, request):
    try:
      employees = Employee.objects.filter(company=request.user.company_profile)
      serializer = EmployeeListSerializer(employees, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({
        "error": str(e),
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeListAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    company_profile = request.user.company_profile
    try:
      employees = Employee.objects.filter(company=company_profile)
      response = []
      for employee in employees:
        response.append({
          'image': employee.image.url,
          'id': employee.id
        })
      return Response({'data': response}, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({
        "error": str(e),
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  @extend_schema(
    request=EmployeeSerializer,
    responses=EmployeeSerializer
  )
  def post(self, request):
    company_profile = request.user.company_profile
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(company=company_profile)
      return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request,pk):
    try:
      employee=Employee.objects.get(pk=pk)
      if not employee.company.user == request.user:
        return Response({
          "error": "You don't have permission to see this employee."
        }, status=status.HTTP_403_FORBIDDEN)
      serializer = EmployeeSerializer(employee)
      return Response({'data':serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({
        "error": str(e),
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  @extend_schema(
    request=EmployeeSerializer,
    responses=EmployeeSerializer
  )
  def patch(self, request, pk):
    try:
      employee=Employee.objects.get(pk=pk)
      serializer = EmployeeSerializer(employee, data=request.data, partial=True)
      if serializer.is_valid():
        serializer.save()
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({
        "error": str(e),
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class ReviewAPIView(APIView):
#   permission_classes = [IsAuthenticated]
#   @extend_schema(
#     request=ReviewSerializer,
#     responses=ReviewSerializer
#   )



