# from django.conf import settings
# from django.shortcuts import render
# from accounts.models import User
# from service_provider.models import CompanyProfile
# from django.contrib.admin.views.decorators import staff_member_required
#
# @staff_member_required
# def dashboard_view(request):
#   context = {
#     "total_users": User.objects.count(),
#     "total_companies": CompanyProfile.objects.count(),
#     "site_title": settings.UNFOLD["SITE_TITLE"],
#     "site_header": settings.UNFOLD["SITE_HEADER"],
#     "sidebar": settings.UNFOLD["SIDEBAR"],
#   }
#   return render(request, "admin/dashboard.html", context)
