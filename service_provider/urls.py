from django.urls import path

from service_provider.views import UnlockJobAPIView

urlpatterns = [
	path('job-unlock/<int:pk>',UnlockJobAPIView.as_view(), name='job-unlock' ),
]