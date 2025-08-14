from django.contrib import admin
from .models import User, PreSubscription
from unfold.admin import ModelAdmin
# Register your models here.



class PreSubscriptionAdmin(ModelAdmin):
  pass
admin.site.register(PreSubscription, PreSubscriptionAdmin)

