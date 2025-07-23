from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Category
from jobs.serializers import JobSerializer, CategorySerializer, CategoryDetailListSerializer


# Create your views here.
class JobAPIView(APIView):
	permission_classes = [IsAuthenticated]
	@extend_schema(
		request=JobSerializer,
		responses={201: None, 400: 'Validation Error'}
	)
	def post(self, request):
		serializer=JobSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save(user=request.user)
			return Response({
				'message': 'Your job has been posted',
				'status': 'success'
			}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryAPIView(APIView):
	permission_classes = [AllowAny]

	def get(self, request):
		categories = Category.objects.all()
		serializer=CategorySerializer(categories,many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryDetailListAPIView(APIView):
	permission_classes = [AllowAny]
	def get(self, request):
		categories = Category.objects.all()
		serializer=CategoryDetailListSerializer(categories,many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)