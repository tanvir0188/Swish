from django.contrib import admin
from .models import User, PreSubscription


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'is_staff')
    search_fields = ('email', 'first_name')
class PreSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'full_name', 'company_name', 'city', 'ice_number', 'formatted_phone_number')
    search_fields = ('email', 'company_name')

    def formatted_phone_number(self, obj):
      if obj.phone_number:
        return f'+{obj.phone_number}'
      else:
        return 'None'


    formatted_phone_number.short_description = 'Phone Number'
admin.site.register(User, UserAdmin)
admin.site.register(PreSubscription, PreSubscriptionAdmin)

