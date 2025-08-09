from rest_framework import serializers
from accounts.models import User
from .models import Message, Room


class UserMinimalSerializer(serializers.ModelSerializer):
  image = serializers.SerializerMethodField()
  full_name = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = ['id', 'full_name', 'email', 'image']

  def get_image(self, obj):
    try:
      return obj.image.url if obj.image else None
    except Exception:
      return None

  def get_full_name(self, obj):
    return obj.full_name or f"{obj.first_name} {obj.last_name}"


class MessageSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
  room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())

  class Meta:
    model = Message
    fields = ['id', 'room', 'text', 'file', 'user', 'seen', 'created_at', 'updated_at']

  def validate(self, data):
    if not data.get('user'):
      raise serializers.ValidationError("User is required")
    if not data.get('room'):
      raise serializers.ValidationError("Room is required")
    return data


class RoomSerializer(serializers.ModelSerializer):
  creator = UserMinimalSerializer(read_only=True)


  class Meta:
    model = Room
    fields = [
      'id',
      'creator',

    ]
    read_only_fields = ['id', 'creator', 'current_users_info']

class RoomListSerializer(serializers.ModelSerializer):
  other_user_name = serializers.SerializerMethodField()
  other_user_image = serializers.SerializerMethodField()
  last_message = serializers.SerializerMethodField()

  class Meta:
    model = Room
    fields = [
      'id',
      'other_user_name',
      'other_user_image',
      'last_message',
    ]

  def get_other_user_name(self, obj):
    request = self.context.get('request')
    other_user = obj.current_users.exclude(id=request.user.id).first()
    return other_user.full_name if other_user else None

  def get_other_user_image(self, obj):
    request = self.context.get('request')
    other_user = obj.current_users.exclude(id=request.user.id).first()
    return other_user.image.url if (other_user and other_user.image) else None

  def get_last_message(self, obj):
    last_msg = obj.messages.order_by('-created_at').first()
    if last_msg:
      return last_msg.text
    other_user = obj.current_users.exclude(id=self.context['request'].user.id).first()
    return f"say hi to {other_user.full_name}" if other_user else None



class RoomDetailSerializer(serializers.ModelSerializer):
  creator = UserMinimalSerializer(read_only=True)
  current_users = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(),
    many=True,
    required=False
  )
  current_users_info = UserMinimalSerializer(
    source='current_users',
    many=True,
    read_only=True
  )
  messages = MessageSerializer(many=True, read_only=True)

  class Meta:
    model = Room
    fields = [
      'id',
      'name',
      'creator',
      'is_private',
      'current_users',
      'current_users_info',
      'messages',
    ]
    read_only_fields = ['id', 'creator', 'current_users_info', 'messages']


class RoomShortListSerializer(serializers.ModelSerializer):
  creator = UserMinimalSerializer(read_only=True)

  class Meta:
    model = Room
    fields = ['id', 'name', 'creator']