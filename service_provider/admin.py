from django.contrib import admin

from jobs.models import Favorite
from service_provider.models import CompanyProfile, Bid, TokenPackage, TokenTransaction

# Register your models here.
admin.site.register(CompanyProfile)
admin.site.register(Bid)
class TokenPackageAdmin(admin.ModelAdmin):
	list_display = ('company', 'package_name', 'package_balance', 'issued_at', 'expires_at', 'is_paid')

admin.site.register(TokenPackage, TokenPackageAdmin)
admin.site.register(TokenTransaction)
class FavoriteAdmin(admin.ModelAdmin):
	list_display = ('user', 'job')

admin.site.register(Favorite, FavoriteAdmin)