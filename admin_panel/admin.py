from django.urls import path
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from django.contrib import admin
from unfold.admin import ModelAdmin
from accounts.models import User
from service_provider.models import CompanyProfile


class DashboardView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Dashboard"  # shown in header
    permission_required = ()  # empty tuple = any staff can see
    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "total_users": User.objects.count(),
            "total_companies": CompanyProfile.objects.count(),
        })
        return context

@admin.register(User)
class UserAdmin(ModelAdmin):
    def get_urls(self):
        custom_view = self.admin_site.admin_view(
            DashboardView.as_view(model_admin=self)
        )
        return [
            path("dashboard/", custom_view, name="dashboard"),
        ] + super().get_urls()


