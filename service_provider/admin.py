from django.contrib import admin

from service_provider.models import CompanyProfile, Bid, TokenPackage, TokenTransaction

# Register your models here.
admin.site.register(CompanyProfile)
admin.site.register(Bid)
admin.site.register(TokenPackage)
admin.site.register(TokenTransaction)