from django.db import models


# Create your models here.

class Category(models.Model):
	name=models.CharField(max_length=100, unique=True, db_index=True)
	category_icon=models.ImageField(upload_to="uploads/category_icons", null=True, blank=True)
	description=models.TextField(null=True, blank=True)
	def __str__(self):
		return self.name
	class Meta:
		verbose_name_plural = 'Categories'
		ordering = ['name']

class SubCategory(models.Model):
	category=models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sub_categories')
	name=models.CharField(max_length=100, unique=True, db_index=True)
	def __str__(self):
		return self.name
	class Meta:
		ordering=['name']
		verbose_name_plural='Sub Categories'


JOB_STATUS_CHOICES = [
    ('Open', 'Open'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
    ('Paused', 'Paused'),
]

class Job(models.Model):
	posted_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
	heading = models.CharField(max_length=255, blank=False, null=False)
	description = models.TextField(blank=False, null=False)
	estimated_time=models.CharField(max_length=100,blank=False, null=False)
	employee_need=models.IntegerField(blank=False, null=False)
	site_photo=models.ImageField(upload_to="uploads/site_photos", null=True, blank=True)
	value=models.FloatField(blank=True, null=True)
	category=models.ForeignKey(Category, on_delete=models.CASCADE, related_name='jobs')
	email=models.EmailField(blank=False, null=False)
	first_name = models.CharField(max_length=100, blank=False, null=False)
	surname = models.CharField(max_length=100, blank=False, null=False)
	telephone_number = models.CharField(max_length=100, blank=False, null=False)
	mission_address=models.CharField(max_length=255, blank=False, null=False)
	postal_code=models.CharField(max_length=20, blank=False, null=False)
	through_swish_or_telephone=models.BooleanField(default=True)
	status=models.CharField(max_length=20, choices=JOB_STATUS_CHOICES, default='open')

	created_at=models.DateTimeField(auto_now_add=True)
	updated_at=models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.heading
	class Meta:
		ordering=['created_at']
		verbose_name_plural = 'jobs'
