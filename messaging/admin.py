from django.contrib import admin
from unfold.admin import ModelAdmin
from messaging.models import Message, Room

# Register your models here.
class MessageAdmin(ModelAdmin):
	pass
admin.site.register(Message, MessageAdmin)
class RoomAdmin(ModelAdmin):
	pass
admin.site.register(Room, RoomAdmin)