from django.contrib import admin
from unfold.admin import ModelAdmin
from jobs.models import Category, Job, SubCategory, JobPauseReason, Area, SiteImage, Review

# Register your models here.
class CategoryAdmin(ModelAdmin):
    fields = ['name','code', 'category_icon', 'description']
    readonly_fields = []
admin.site.register(Category, CategoryAdmin)
class SubCategoryAdmin(ModelAdmin):
    pass
admin.site.register(SubCategory, SubCategoryAdmin)
class JobAdmin(ModelAdmin):
    list_display = ('heading', 'posted_by', 'category','area', 'custom_category', 'value', 'created_at')
    list_per_page = 20  # number of jobs per page
class SiteImageAdmin(ModelAdmin):
    pass
admin.site.register(SiteImage, SiteImageAdmin)
admin.site.register(Job, JobAdmin)
class JobPauseReasonAdmin(ModelAdmin):
    pass
admin.site.register(JobPauseReason, JobPauseReasonAdmin)
class AreaAdmin(ModelAdmin):
    pass
admin.site.register(Area, AreaAdmin)
class ReviewAdmin(ModelAdmin):
    pass
admin.site.register(Review, ReviewAdmin)
