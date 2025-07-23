from django.urls import path

from jobs.views import JobAPIView, CategoryAPIView, CategoryDetailListAPIView

urlpatterns = [
	path('job', JobAPIView.as_view(), name='job-creation'),
	path('category', CategoryAPIView.as_view(), name='categories'),
	path('category-list', CategoryDetailListAPIView.as_view(), name='category-list'),
]