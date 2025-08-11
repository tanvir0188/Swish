from django.urls import path

from messaging.views import RoomCreateAPIView, RoomListAPIView, RoomMessageView, ActiveRoomListAPIView, \
    UnreadRoomListAPIView

urlpatterns = [
    path('room-list/', RoomListAPIView.as_view(), name='room-list'),        # for GET list
    path('room-list/active', ActiveRoomListAPIView.as_view(), name='active-room-list'),
    path('room-list/unread', UnreadRoomListAPIView.as_view(), name='unread-room-list'),
    path('room/<int:pk>/', RoomCreateAPIView.as_view(), name='room-create'),  # for POST create with user id
    path('room-messages/<int:pk>', RoomMessageView.as_view(), name='room-messages'),
]