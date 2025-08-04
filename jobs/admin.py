from django.contrib import admin

from jobs.models import Category, Job, SubCategory, JobPauseReason, Area, SiteImage

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
class JobAdmin(admin.ModelAdmin):
    list_display = ('heading', 'posted_by', 'category','area', 'custom_category', 'value', 'created_at')
    list_per_page = 20  # number of jobs per page
admin.site.register(SiteImage)
admin.site.register(Job, JobAdmin)
admin.site.register(JobPauseReason)
admin.site.register(Area)
