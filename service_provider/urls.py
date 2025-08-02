from django.urls import path

from service_provider.views import UnlockJobAPIView, CompanyRegisterAPIView, add_area, add_work_type

urlpatterns = [
	path('job-unlock/<int:pk>',UnlockJobAPIView.as_view(), name='job-unlock' ),
	path('companyprofile', CompanyRegisterAPIView.as_view(), name='company-profile' ),
	path('add-area',add_area, name='add-area' ),
	path('add-work-type', add_work_type, name='add-work-type' ),
	# path('company-registration',CompanyRegisterAPIView.as_view(), name='company-registration' )
]