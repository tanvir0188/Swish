from django.contrib import admin
from .models import User, PreSubscription


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name','surname', 'is_staff')
    search_fields = ('email', 'first_name')
    
admin.site.register(User, UserAdmin)
admin.site.register(PreSubscription)

