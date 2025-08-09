import json

import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from .models import Room, Message
from .serializers import MessageSerializer
redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)



class ChatConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.room_id = self.scope['url_route']['kwargs']['room_id']
    self.room_group_name = f'chat_{self.room_id}'
    self.user = self.scope['user']

    if self.user.is_anonymous:
      await self.close()
      return

    room_exists = await self.check_room_access()
    if not room_exists:
      await self.close()
      return

    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )

    await self.accept()

    # Add this user to Redis set for connected users in this room
    redis_key = f"room_{self.room_id}_connected"
    # Run in threadpool since redis-py is sync
    await database_sync_to_async(redis_client.sadd)(redis_key, str(self.user.id))
    await self.mark_all_messages_seen_if_both_connected()
    # Optionally, get the count of connected users
    connected_count = await database_sync_to_async(redis_client.scard)(redis_key)

    print(f"Users connected in room {self.room_id}: {connected_count}")

    # Now you can act on connected_count if you want

    await self.send_existing_messages()

  async def disconnect(self, close_code):
    redis_key = f"room_{self.room_id}_connected"
    await database_sync_to_async(redis_client.srem)(redis_key, str(self.user.id))
    await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

  async def receive(self, text_data):
    try:
      text_data_json = json.loads(text_data)
      message_type = text_data_json.get('type', 'chat_message')

      if message_type == 'chat_message':
        message_text = text_data_json.get('message', '')

        if not message_text.strip():
          await self.send(text_data=json.dumps({
            'type': 'error',
            'message': 'Message cannot be empty'
          }))
          return

        # Prepare data for serializer
        data = {'text': message_text}
        # Save message to database
        message = await self.save_message(data)

        if message:
          # Serialize the message
          message_data = await self.serialize_message(message)

          # Send message to both users in the private room
          await self.channel_layer.group_send(
            self.room_group_name,
            {
              'type': 'chat_message',
              'message_data': message_data
            }
          )

      elif message_type == 'get_messages':
        # Send existing messages
        await self.send_existing_messages()

    except json.JSONDecodeError:
      await self.send(text_data=json.dumps({
        'type': 'error',
        'message': 'Invalid JSON format'
      }))
    except Exception as e:
      await self.send(text_data=json.dumps({
        'type': 'error',
        'message': f'An error occurred: {str(e)}'
      }))

  async def chat_message(self, event):
    message_data = event['message_data']

    # Send message to WebSocket
    await self.send(text_data=json.dumps({
      'type': 'chat_message',
      'message': message_data
    }))

  @database_sync_to_async
  def mark_all_messages_seen_if_both_connected(self):
    room_id = self.room_id

    # Get room user IDs
    try:
      room = Room.objects.get(pk=room_id)
      user_ids = list(room.current_users.values_list('id', flat=True))
    except Room.DoesNotExist:
      return False

    redis_key = f"room_{room_id}_connected"
    connected_user_ids = redis_client.smembers(redis_key)
    connected_user_ids = set(map(int, connected_user_ids))

    if set(user_ids).issubset(connected_user_ids) and len(user_ids) == 2:
      # Update all unseen messages to seen=True
      room.messages.filter(seen=False).update(seen=True)
      return True
    return False
  @database_sync_to_async
  def check_room_access(self):
    """Check if room exists, is private, and user has access to it"""
    try:
      room = Room.objects.get(pk=self.room_id)
      # Ensure the room is private and has exactly 2 users
      if not room.is_private or room.current_users.count() != 2:
        return False
      # Check if user is in the room or is the creator
      return (self.user in room.current_users.all() or room.creator == self.user)
    except Room.DoesNotExist:
      return False

  @database_sync_to_async
  def save_message(self, data):
    """Save message and set seen=True if both users connected."""
    try:
      room = Room.objects.get(pk=self.room_id)
      if not room.is_private or room.current_users.count() != 2:
        return None
      if self.user not in room.current_users.all() and room.creator != self.user:
        return None

      # Check if both connected (using the Redis presence set)
      redis_key = f"room_{self.room_id}_connected"
      connected_user_ids = redis_client.smembers(redis_key)
      connected_user_ids = set(map(int, connected_user_ids))

      room_user_ids = set(room.current_users.values_list('id', flat=True))

      both_connected = room_user_ids.issubset(connected_user_ids)

      data['user'] = self.user.id
      data['room'] = room.id

      # Mark new message as seen if both connected
      if both_connected:
        data['seen'] = True

      serializer = MessageSerializer(data=data)
      if serializer.is_valid():
        message = serializer.save()

        # Mark all old messages as seen if both connected
        if both_connected:
          room.messages.filter(seen=False).update(seen=True)

        return message
      else:
        return None
    except Room.DoesNotExist:
      return None

  @database_sync_to_async
  def serialize_message(self, message):
    """Serialize message using MessageSerializer"""
    serializer = MessageSerializer(message)
    return serializer.data

  @database_sync_to_async
  def get_room_messages(self):
    """Get all messages for the private room"""
    try:
      room = Room.objects.get(pk=self.room_id)
      if not room.is_private or room.current_users.count() != 2:
        return []
      messages = Message.objects.filter(room=room).order_by('created_at')
      serializer = MessageSerializer(messages, many=True)
      return serializer.data
    except Room.DoesNotExist:
      return []

  async def send_existing_messages(self):
    """Send existing messages to the user"""
    messages = await self.get_room_messages()
    await self.send(text_data=json.dumps({
      'type': 'message_history',
      'messages': messages
    }))