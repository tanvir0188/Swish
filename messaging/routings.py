# chat/routing.py
from django.urls import path

from messaging import consummers

websocket_urlpatterns = [
    path('ws/chat/<int:room_id>/', consummers.ChatConsumer.as_asgi()),
]