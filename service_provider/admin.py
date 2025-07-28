from django.contrib import admin

from service_provider.models import CompanyProfile, Bid

# Register your models here.
admin.site.register(CompanyProfile)
admin.site.register(Bid)