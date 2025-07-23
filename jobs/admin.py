from django.contrib import admin

from jobs.models import Category, Job, SubCategory

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Job)