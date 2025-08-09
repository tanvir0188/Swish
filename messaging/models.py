from django.db import models
from accounts.models import User

class Room(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)
	creator = models.ForeignKey(
		User, on_delete=models.CASCADE, related_name="created_rooms"
	)
	is_private = models.BooleanField(default=True)
	current_users = models.ManyToManyField(User, related_name="current_rooms", blank=True)

	def __str__(self):
		return f"Room({self.name})"

class Message(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
	text = models.TextField(blank=True, null=True, max_length=1000)
	file = models.FileField(blank=True, null=True, upload_to="messages")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
	seen = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Message({self.user} in {self.room})"

class Notification(models.Model):
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
	message = models.ForeignKey(Message, on_delete=models.CASCADE)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"To {self.recipient} about Message {self.message.id}"