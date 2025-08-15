from django.contrib import admin
from unfold.admin import ModelAdmin

from jobs.models import Favorite
from service_provider.models import CompanyProfile, Bid, TokenPackage, TokenTransaction

class BidAdmin(ModelAdmin):
	list_display = ('job', 'bidding_company', 'status')
	list_filter = ('status',)
	search_fields = ['job__heading']
admin.site.register(Bid, BidAdmin)
class TokenPackageAdmin(ModelAdmin):
	list_display = ('company', 'package_name', 'package_balance', 'issued_at', 'expires_at', 'is_paid')

admin.site.register(TokenPackage, TokenPackageAdmin)
class TokenTransactionAdmin(ModelAdmin):
	list_display = ('package', 'job', 'used_by', 'used_at')
admin.site.register(TokenTransaction, TokenTransactionAdmin)
class FavoriteAdmin(ModelAdmin):
	list_display = ('user', 'job')

admin.site.register(Favorite, FavoriteAdmin)