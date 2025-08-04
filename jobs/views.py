from django.db.models import Prefetch
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import serializer

from accounts.models import User
from jobs.models import Category, SubCategory, Job, JobPauseReason, SiteImage
from jobs.serializers import JobSerializer, CategorySerializer, CategoryDetailListSerializer, AddSubCategorySerializer, \
  BidStatusUpdateSerializer, ReviewSerializer, JobPausingReasonSerializer
from service_provider.models import Bid


# Create your views here.
class JobAPIView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request=JobSerializer,
    responses={201: None, 400: 'Validation Error'}
  )
  def post(self, request):
    if request.user.role != 'private':
      return Response({'error': 'Login as private account to post job'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = JobSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
      job = serializer.save(posted_by=request.user)
      return Response({
        'message': 'Your job has been posted',
        'status': 'success'
      }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryAPIView(APIView):
  permission_classes = [AllowAny]

  def get(self, request):
    categories = Category.objects.prefetch_related('sub_categories').all()
    serializer=CategorySerializer(categories,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryDetailListAPIView(APIView):
  permission_classes = [AllowAny]
  def get(self, request):
    categories = Category.objects.all()
    serializer=CategoryDetailListSerializer(categories,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# has to be deleted
class BulkSubCategoryAPIView(APIView):
  permission_classes = [AllowAny]
  @extend_schema(
    request=AddSubCategorySerializer,
    responses={200: None, 400: 'Validation error'}
  )

  def post(self, request):
    serializer = AddSubCategorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    category_id = serializer.validated_data['category']
    name_list = serializer.validated_data['name']

    category = Category.objects.get(id=category_id)

    subcategories = [
      SubCategory(name=name, category=category) for name in name_list
    ]
    SubCategory.objects.bulk_create(subcategories)

    return Response({"detail": "Subcategories created."}, status=status.HTTP_200_OK)

@api_view(['get'])
@permission_classes([IsAuthenticated])
def my_job_posts(request):
  try:
    if request.user.role != 'private':
      return Response({'error':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    jobs = Job.objects.filter(posted_by=request.user) \
      .prefetch_related(
      Prefetch(
        'bid_set',
        queryset=Bid.objects.select_related('bidding_company')
      )
    )

    response = []

    for job in jobs:
      bidder_response = [
        {
          'id': bidder.id,
          'company_name': bidder.bidding_company.company_profile.company_name,
          'company_user_id': bidder.bidding_company.id,
          'proposal_description': bidder.proposal_description,
          'telephone': bidder.bidding_company.telephone,
          'status': bidder.status,
          'amount': bidder.amount,
          'timeline': bidder.time_estimate,
          'placed': bidder.created_at
        }
        for bidder in job.bid_set.all()
      ]

      response.append({
        'id': job.id,
        'heading': job.heading,
        'description': job.description,
        'posted': job.created_at,
        'status': job.status,
        'bids': len(bidder_response),
        'bidder_response': bidder_response
      })

    return Response({
      'status': 'success',
      'jobs': response
    }, status=status.HTTP_200_OK)

  except Exception as e:
    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
  methods=["PATCH"],
  request=BidStatusUpdateSerializer,
  responses={
    200: BidStatusUpdateSerializer,
    400: OpenApiExample("Bad Request", value={"error": "Missing bid_id"}),
    403: OpenApiExample("Forbidden", value={"error": "Unauthorized"}),
    404: OpenApiExample("Not Found", value={"error": "Job not found"}),
  },
  description="Change the status of a bid for a given job. Also updates the job status to 'In Progress'.",
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_bid_status(request, pk):
  try:
    bid = Bid.objects.get(pk=pk)
    job = bid.job

    # Only job owner can update the bid status
    if job.posted_by != request.user:
      return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    # Reject further bidding if job is no longer open
    if job.status in ['In Progress', 'Completed', 'Paused']:
      return Response({'error': f'Cannot update bid. Job is already {job.status}.'},
                      status=status.HTTP_400_BAD_REQUEST)

    serializer = BidStatusUpdateSerializer(bid, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()

      # Update job status based on bid status
      bid_status = serializer.validated_data.get('status')
      if bid_status == 'Complete':
        job.status = 'In Progress'
        job.save()
      elif bid_status == 'Rejected':
        job.status = 'Open'
        job.save()

      return Response({'message': 'Bid status updated', 'bid': bid.status, 'job_status': job.status},
                      status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  except Bid.DoesNotExist:
    return Response({'error': 'Bid not found'}, status=status.HTTP_404_NOT_FOUND)
  except Exception as e:
    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def patch_job_status(request, pk):
  try:
    job = Job.objects.get(pk=pk)
    if job.posted_by != request.user:
      return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    job.status='Paused'
    job.save()
    return Response({'message': 'Job status paused', 'status': job.status}, status=status.HTTP_200_OK)
  except Exception as e:
    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job(request, pk):
  try:
    job = Job.objects.get(pk=pk)
    if job.posted_by == request.user:
      job.delete()
      return Response({'message':'Job deleted'},status=status.HTTP_200_OK)
    return Response({'error':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
  except Exception as e:
    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReviewAPIView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request=ReviewSerializer,
    responses={200: None, 400: 'Validation error'}
  )
  def post(self, request, pk):
    try:
      service_provider = User.objects.get(id=pk)
      if service_provider.role != 'company':
        return Response({'error': 'Only users with company role can receive reviews.'},
                        status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
      return Response({'error': 'Service provider not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role != 'private':
      return Response({'error': 'Only private users can post reviews.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(user=request.user, service_provider=service_provider)
      return Response({'message': 'Review posted successfully.'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobPausingReasonAPIView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request=JobPausingReasonSerializer,
    responses={200: None, 400: 'Validation error'}
  )
  def post(self, request, pk):
    try:
      job = Job.objects.get(pk=pk)

      if job.posted_by != request.user:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

      if job.status != 'Paused':
        return Response({'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

      # Update if already exists, else create
      reason_instance = JobPauseReason.objects.filter(job=job).first()

      if reason_instance:
        serializer = JobPausingReasonSerializer(reason_instance, data=request.data)
      else:
        serializer = JobPausingReasonSerializer(data=request.data)

      if serializer.is_valid():
        serializer.save(job=job)
        return Response({'message': 'Thanks for your feedback.'}, status=status.HTTP_201_CREATED)

      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
