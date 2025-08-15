from datetime import timedelta

from django.db.models import Count, OuterRef, Exists, Min, Q, F
from django.urls import path
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from django.contrib import admin
from unfold.admin import ModelAdmin
from accounts.models import User
from service_provider.models import CompanyProfile, TokenPackage, Bid, TokenTransaction


class DashboardView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Dashboard"  # shown in header
    permission_required = ()  # empty tuple = any staff can see
    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Free token stats
        free_users = User.objects.filter(
            token_packages__package_name='Starter',
            token_packages__is_paid=False
        )

        total_free_users = free_users.count()

        free_users_used_all_token = User.objects.filter(
            token_packages__package_name='Starter',
            token_packages__is_paid=False,
            token_packages__package_balance=0
        ).count()
        print(total_free_users)
        percent_used_all_token = (free_users_used_all_token / total_free_users) * 100

        # 1️⃣ Users with free Starter packages and less than 40 tokens
        free_users_with_used_tokens = User.objects.filter(
            token_packages__package_name='Starter',
            token_packages__is_paid=False,
            token_packages__package_balance__lt=40
        )
        print(free_users_with_used_tokens.count())

        # 2️⃣ Users who have token transactions
        #     where the related job has a bid from the same user that is Rejected or Active
        users_with_incompleted_bids = User.objects.filter(
            id__in=Bid.objects.filter(
                status__in=['Rejected', 'Active'],
                bidding_company__in=free_users_with_used_tokens,
                job__token_transaction__used_by=F('bidding_company')
            ).values_list('bidding_company', flat=True)
        ).distinct()

        count_users_with_incompleted_bids = users_with_incompleted_bids.count()
        print(count_users_with_incompleted_bids)
        percent_users_with_incomplete_bids = (count_users_with_incompleted_bids / free_users_with_used_tokens.count()) * 100



        context.update({
            "percent_used_all_tokens": percent_used_all_token,
            "percent_used_some_never_converted": percent_users_with_incomplete_bids,
            "avg_time_to_first_token": 14,
            "avg_time_to_first_purchase": 17,
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


