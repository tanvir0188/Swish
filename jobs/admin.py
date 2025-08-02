from django.contrib import admin

from jobs.models import Category, Job, SubCategory, JobPauseReason, Area

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Job)
admin.site.register(JobPauseReason)
admin.site.register(Area)