from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema

from accounts.models import User
from .models import Room, Message
from .serializers import RoomSerializer, RoomDetailSerializer, MessageSerializer, RoomListSerializer



class RoomCreateAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		description="Create a private room between the authenticated user and another user by their ID.",
		responses={201: 'Room created successfully', 404: 'User not found'}
	)
	def post(self, request, pk):
		# Get the other user or return 404
		another_user = get_object_or_404(User, pk=pk)

		# Prevent creating a room with self
		if another_user == request.user:
			return Response({'error': 'Cannot create a room with yourself.'}, status=status.HTTP_400_BAD_REQUEST)

		# Check if a private room already exists between these two users
		existing_rooms = Room.objects.filter(
			is_private=True,
			current_users=request.user
		).filter(
			current_users=another_user
		).distinct()

		if existing_rooms.exists():
			room = existing_rooms.first()
			return Response({'room_id': room.id, 'message': 'Room already exists'}, status=status.HTTP_200_OK)

		# Create a new room
		room = Room.objects.create(
			creator=request.user,
			is_private=True,
			name=f'{request.user.full_name or (request.user.first_name + " " + request.user.last_name)} - {another_user.full_name or (another_user.first_name + " " + another_user.last_name)}'
		)
		room.current_users.add(request.user, another_user)
		if room.is_private and room.current_users.count() > 2:
			room.delete()
			return Response({'error': 'Private rooms can only have 2 participants.'}, status=400)
		# Validate the number of users after adding
		if room.is_private and room.current_users.count() > 2:
			room.delete()
			return Response({'error': 'Private room cannot have more than 2 users.'}, status=status.HTTP_400_BAD_REQUEST)

		# Save if you want to update timestamps or trigger other logic
		room.save()

		return Response({'room_id': room.id, 'message': 'Room created successfully'}, status=status.HTTP_201_CREATED)

class RoomListAPIView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		rooms = Room.objects.filter(
			Q(creator=request.user) |
			Q(current_users=request.user)
		).distinct().order_by('-id')

		serializer = RoomListSerializer(rooms, many=True, context={'request': request})
		return Response({
			'rooms': serializer.data,
			'status': 'success'
		}, status=status.HTTP_200_OK)

class RoomDetailView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		request=RoomDetailSerializer,
		responses={200: RoomDetailSerializer, 404: 'Not found'}
	)
	def get(self, request, pk):
		room = get_object_or_404(Room, pk=pk)

		# permission: user must be participant or creator
		if not (room.creator == request.user or room.current_users.filter(id=request.user.id).exists()):
			return Response({'error': 'You do not have access to this room.'}, status=status.HTTP_403_FORBIDDEN)

		serializer = RoomDetailSerializer(room)
		return Response({
			'room': serializer.data,
			'status': 'success'
		}, status=status.HTTP_200_OK)

	@extend_schema(
		request=RoomDetailSerializer,
		responses={200: RoomDetailSerializer, 400: 'Validation Error', 403: 'Forbidden', 404: 'Not found'}
	)
	def patch(self, request, pk):
		room = get_object_or_404(Room, pk=pk)

		# Only the creator can modify room metadata (name/is_private/current_users etc.)
		if room.creator != request.user:
			return Response({'error': 'Only the room creator can update the room.'}, status=status.HTTP_403_FORBIDDEN)

		serializer = RoomDetailSerializer(room, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({
				'room': serializer.data,
				'status': 'success'
			}, status=status.HTTP_200_OK)

		return Response({
			'room': serializer.errors,
			'status': 'error'
		}, status=status.HTTP_400_BAD_REQUEST)

class MessagePagination(PageNumberPagination):
	page_size = 50

class RoomMessageView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		request=MessageSerializer,
		responses={200: MessageSerializer(many=True), 201: MessageSerializer, 400: 'Validation Error', 403: 'Forbidden'}
	)
	def get(self, request, pk):
		room = get_object_or_404(Room, pk=pk)

		# permission: user must be participant or creator
		if not (room.creator == request.user or room.current_users.filter(id=request.user.id).exists()):
			return Response({'error': 'You do not have access to this room.'}, status=status.HTTP_403_FORBIDDEN)
		messages_qs = Message.objects.filter(room=room).order_by('created_at')

		paginator = MessagePagination()
		page = paginator.paginate_queryset(messages_qs, request)
		serializer = MessageSerializer(page, many=True)
		return paginator.get_paginated_response(serializer.data)

	def post(self, request, pk):
		room = get_object_or_404(Room, pk=pk)

		# permission: user must be participant or creator to post a message
		if not (room.creator == request.user or room.current_users.filter(id=request.user.id).exists()):
			return Response({'error': 'You do not have access to this room.'}, status=status.HTTP_403_FORBIDDEN)

		serializer = MessageSerializer(data=request.data)
		if serializer.is_valid():
			message = serializer.save(user=request.user, room=room)
			out_serializer = MessageSerializer(message)
			return Response({'message': out_serializer.data, 'status': 'success'}, status=status.HTTP_201_CREATED)

		return Response({'message': serializer.errors, 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
