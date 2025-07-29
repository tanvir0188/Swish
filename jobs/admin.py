from django.contrib import admin

from jobs.models import Category, Job, SubCategory, JobPauseReason

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Job)
admin.site.register(JobPauseReason)
