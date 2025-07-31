from django.urls import path

from service_provider.views import UnlockJobAPIView, CompanyRegisterAPIView

urlpatterns = [
	path('job-unlock/<int:pk>',UnlockJobAPIView.as_view(), name='job-unlock' ),
	path('companyprofile', CompanyRegisterAPIView.as_view(), name='company-profile' ),
	# path('company-registration',CompanyRegisterAPIView.as_view(), name='company-registration' )
]