from django.urls import path

from jobs.views import JobAPIView, CategoryAPIView, CategoryDetailListAPIView, BulkSubCategoryAPIView, my_job_posts, \
	change_bid_status, patch_job_status, delete_job

urlpatterns = [
	path('job', JobAPIView.as_view(), name='job-creation'),
	path('job/<int:pk>', delete_job, name='job-deletion'),
	path('category', CategoryAPIView.as_view(), name='categories'),
	path('category-list', CategoryDetailListAPIView.as_view(), name='category-list'),
	path('sub-category', BulkSubCategoryAPIView.as_view(), name='sub-category'),
	path('my-jobs', my_job_posts, name='my-jobs'),
	path('bid-status/<int:pk>', change_bid_status, name='bid-status'),
	path('job-status/<int:pk>', patch_job_status, name='job-status'),
]