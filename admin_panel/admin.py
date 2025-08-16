from datetime import timedelta

from django.db.models import  Min, F, ExpressionWrapper, DurationField, Avg
from django.urls import path
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from django.contrib import admin
from unfold.admin import ModelAdmin
from accounts.models import User
from service_provider.models import  Bid
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek
from service_provider.models import Job


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
        users_with_first_token = (
            User.objects
            .filter(token_transactions__package__package_name="Starter",
                    token_transactions__package__is_paid=False)
            .annotate(first_token_used_at=Min("token_transactions__used_at"))
            .exclude(first_token_used_at=None)  # only keep those with a transaction
            .annotate(
                time_to_first_token=ExpressionWrapper(
                    F("first_token_used_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
        )

        # Step 2: Compute the average time
        avg_time_to_first_token = users_with_first_token.aggregate(
            avg_time_to_first_token=Avg("time_to_first_token")
        )["avg_time_to_first_token"]
        if avg_time_to_first_token:
            # Remove microseconds
            avg_time_to_first_token = avg_time_to_first_token - timedelta(microseconds=avg_time_to_first_token.microseconds)

        # 🔹 Jobs per day
        jobs_per_day_qs = (
            Job.objects.annotate(day=TruncDay("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        jobs_per_day = {
            "labels": [f"{j['day'].strftime('%Y-%m-%d')} ({j['count']})" for j in jobs_per_day_qs],
            "datasets": [
                {"label": "Jobs per Day", "data": [j["count"] for j in jobs_per_day_qs]}
            ],
        }

        # 🔹 Jobs per week
        jobs_per_week_qs = (
            Job.objects.annotate(week=TruncWeek("created_at"))
            .values("week")
            .annotate(count=Count("id"))
            .order_by("week")
        )

        jobs_per_week = {
            "labels": [f"{j['week'].strftime('%Y-%m-%d')} ({j['count']})" for j in jobs_per_week_qs],
            "datasets": [
                {"label": "Jobs per Week", "data": [j["count"] for j in jobs_per_week_qs]}
            ],
        }

        context.update({
            "percent_used_all_tokens": percent_used_all_token,
            "percent_used_some_never_converted": percent_users_with_incomplete_bids,
            "avg_time_to_first_token": avg_time_to_first_token,
            "avg_time_to_first_purchase": 17,
            "jobs_per_day":jobs_per_day,
            "jobs_per_week": jobs_per_week
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


