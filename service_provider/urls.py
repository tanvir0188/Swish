from django.urls import path

from service_provider.views import UnlockJobAPIView, CompanyRegisterAPIView, add_area, add_work_type, \
	ToggleFavoriteAPIView, SideBarInfoAPIView, filtered_all_job_list, filtered_new_job_list, filtered_favorite_job_list, \
	filtered_responded_job_list, filtered_won_job_list

urlpatterns = [
	path('job-unlock/<int:pk>',UnlockJobAPIView.as_view(), name='job-unlock' ),
	path('companyprofile', CompanyRegisterAPIView.as_view(), name='company-profile' ),
	path('add-area',add_area, name='add-area' ),
	path('add-work-type', add_work_type, name='add-work-type' ),
	path('toggle-favorite', ToggleFavoriteAPIView.as_view(), name='toggle-favorite' ),
	path('filtered-all-jobs/', filtered_all_job_list, name='filtered-all-jobs' ),
	path('filtered-new-jobs/', filtered_new_job_list, name='filtered-new-jobs'),
	path('filtered-favorite-jobs/', filtered_favorite_job_list, name='filtered-favorite-jobs'),
	path('filtered-responded-jobs/', filtered_responded_job_list, name='filtered-responded-jobs'),
	path('filtered-won-jobs/', filtered_won_job_list, name='filtered-won-jobs'),
	path('filter-bar', SideBarInfoAPIView.as_view(), name='filter-bar' ),
	# path('company-registration',CompanyRegisterAPIView.as_view(), name='company-registration' )
]