from django.urls import path

from messaging.views import RoomCreateAPIView, RoomListAPIView

urlpatterns = [
    path('room-list', RoomListAPIView.as_view(), name='room-list'),        # for GET list
    path('room/<int:pk>/', RoomCreateAPIView.as_view(), name='room-create'),  # for POST create with user id
]