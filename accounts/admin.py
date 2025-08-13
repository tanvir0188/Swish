from django.contrib import admin
from .models import User, PreSubscription
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
# Register your models here.


class UserAdmin(ModelAdmin):
  list_display = ('email', 'first_name','surname', 'is_staff')
  search_fields = ('email', 'first_name')
  change_password_form=AdminPasswordChangeForm

admin.site.register(User, UserAdmin)
class PreSubscriptionAdmin(ModelAdmin):
  pass
admin.site.register(PreSubscription, PreSubscriptionAdmin)

