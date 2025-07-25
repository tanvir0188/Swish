from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Category, SubCategory
from jobs.serializers import JobSerializer, CategorySerializer, CategoryDetailListSerializer, AddSubCategorySerializer


# Create your views here.
class JobAPIView(APIView):
  permission_classes = [IsAuthenticated]
  @extend_schema(
    request=JobSerializer,
    responses={201: None, 400: 'Validation Error'}
  )
  def post(self, request):
    serializer=JobSerializer(data=request.data)
    if request.user.role == 'private':
      if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({
          'message': 'Your job has been posted',
          'status': 'success'
        }, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'Login as private account to post job'}, status=status.HTTP_400_BAD_REQUEST)


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

class BulkSubCategoryAPIView(APIView):
  permission_classes = [AllowAny]
  @extend_schema(
    request=AddSubCategorySerializer,
    responses={200: None, 400: 'Validation error'}
  )

  def post(self, request):  # ⚠️ Use lowercase 'post'
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