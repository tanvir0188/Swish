from django.urls import path

from service_provider.views import UnlockJobAPIView, CompanyRegisterAPIView, add_area, add_work_type, \
	ToggleFavoriteAPIView, SideBarInfoAPIView, filtered_job_list, JobDetailAPIView, CompanyBiddingAPIView

urlpatterns = [
	path('job-unlock/<int:pk>',UnlockJobAPIView.as_view(), name='job-unlock' ),
	path('companyprofile', CompanyRegisterAPIView.as_view(), name='company-profile' ),
	path('add-area',add_area, name='add-area' ),
	path('add-work-type', add_work_type, name='add-work-type' ),
	path('toggle-favorite', ToggleFavoriteAPIView.as_view(), name='toggle-favorite' ),
	path('filtered-job-list/', filtered_job_list, name='filtered-job-list'),
	path('job-detail/<int:pk>',JobDetailAPIView.as_view(), name='job-detail' ),
	path('filter-bar', SideBarInfoAPIView.as_view(), name='filter-bar' ),
	path('bidding-in-job/<int:pk>', CompanyBiddingAPIView.as_view(), name='bidding-in-job' ),
	# path('company-registration',CompanyRegisterAPIView.as_view(), name='company-registration' )\
]