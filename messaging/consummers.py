import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from .models import Room, Message
from .serializers import MessageSerializer



class ChatConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.room_id = self.scope['url_route']['kwargs']['room_id']
    self.room_group_name = f'chat_{self.room_id}'
    self.user = self.scope['user']

    # Check if user is authenticated
    if self.user.is_anonymous:
      await self.close()
      return

    # Check if room exists and user has access
    room_exists = await self.check_room_access()
    if not room_exists:
      await self.close()
      return

    # Join room group (used for broadcasting to both users)
    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )

    await self.accept()

    # Send existing messages to the newly connected user
    await self.send_existing_messages()

  async def disconnect(self, close_code):
    # Leave room group
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )

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
    """Save message to database for the private room"""
    try:
      room = Room.objects.get(pk=self.room_id)
      # Verify room is private and has exactly 2 users
      if not room.is_private or room.current_users.count() != 2:
        return None
      if self.user not in room.current_users.all() and room.creator != self.user:
        return None

      data['user'] = self.user.id
      data['room'] = room.id

      serializer = MessageSerializer(data=data)
      if serializer.is_valid():
        return serializer.save()
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