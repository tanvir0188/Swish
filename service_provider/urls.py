from django.urls import path

from service_provider.views import UnlockJobAPIView, CompanyProfileAPIView, add_area, add_work_type, \
	ToggleFavoriteAPIView, SideBarInfoAPIView, filtered_job_list, JobDetailAPIView, CompanyBiddingAPIView, \
	EditSubCategoryAPIView, patch_company_profile, CompanyProfileDetailAPIView, get_company_cat_and_sub_cat, \
	CompanyLogoAndWallpaperAPIView, EmployeeApiView, EmployeeDetailAPIView, EmployeeListAPIView

urlpatterns = [
	path('job-unlock/<int:pk>',UnlockJobAPIView.as_view(), name='job-unlock' ),
	path('companyprofile', CompanyProfileAPIView.as_view(), name='company-profile' ),
	path('partial-company-profile', patch_company_profile, name='patch-company-profile' ),
	path('company-profile-detail', CompanyProfileDetailAPIView.as_view(), name='company-profile-detail' ),
	path('company-sub-categories', get_company_cat_and_sub_cat, name='company-sub-categories' ),
	path('company-logo-wallpaper', CompanyLogoAndWallpaperAPIView.as_view(), name='company-logo-wallpaper' ),
	path('sub-category', EditSubCategoryAPIView.as_view(), name='sub-category' ),
	path('add-area',add_area, name='add-area' ),
	path('add-work-type', add_work_type, name='add-work-type' ),
	path('toggle-favorite', ToggleFavoriteAPIView.as_view(), name='toggle-favorite' ),
	path('filtered-job-list/', filtered_job_list, name='filtered-job-list'),
	path('job-detail/<int:pk>',JobDetailAPIView.as_view(), name='job-detail' ),
	path('filter-bar', SideBarInfoAPIView.as_view(), name='filter-bar' ),
	path('bidding-in-job/<int:pk>', CompanyBiddingAPIView.as_view(), name='bidding-in-job' ),
	path('employee-list', EmployeeApiView.as_view(), name='employee-list' ),
	path('employees/', EmployeeListAPIView.as_view(), name='employee-list-create'),
	path('employees/<int:pk>/', EmployeeDetailAPIView.as_view(), name='employee-detail'),
	# path('company-registration',CompanyRegisterAPIView.as_view(), name='company-registration' )\
]