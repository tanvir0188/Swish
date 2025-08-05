from django.core.exceptions import ValidationError
from django.db import models
from multiselectfield import MultiSelectField


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
  category=models.ForeignKey(Category, on_delete=models.SET_NULL,null=True, related_name='sub_categories')
  name=models.CharField(max_length=100, unique=True, db_index=True)
  def __str__(self):
    return self.name
  class Meta:
    ordering=['name']
    verbose_name_plural='Sub Categories'

class CustomCategory(models.Model):
  name=models.CharField(max_length=100, unique=True, db_index=True)
  def __str__(self):
    return self.name
  class Meta:
    ordering=['name']
    verbose_name_plural='Custom Categories'

class Favorite(models.Model):
  user=models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='favorites')
  job=models.ForeignKey('Job', on_delete=models.CASCADE, related_name='favorited_by')
  class Meta:
    unique_together = ('user', 'job')

  def __str__(self):
    return f'{self.user.username} - {self.job.heading}'


JOB_STATUS_CHOICES = [
    ('Open', 'Open'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
    ('Paused', 'Paused'),
]
JOB_SIZE_CHOICES = [
  ('Small', 'Small'),
  ('Regular', 'Regular'),
  ('Large', 'Large'),
]

class Job(models.Model):
  posted_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
  heading = models.CharField(max_length=255, blank=False, null=False)
  description = models.TextField(blank=False, null=False)
  estimated_time = models.CharField(max_length=100, blank=False, null=False)
  employee_need = models.IntegerField(blank=False, null=False)
  area = models.ForeignKey('Area', on_delete=models.CASCADE, related_name='job_areas')
  value = models.FloatField(blank=True, null=True)
  category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='jobs')
  custom_category = models.ForeignKey(CustomCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
  size = models.CharField(max_length=10, choices=JOB_SIZE_CHOICES, null=True, blank=True)
  email = models.EmailField(blank=False, null=False)
  first_name = models.CharField(max_length=100, blank=False, null=False)
  surname = models.CharField(max_length=100, blank=False, null=False)
  telephone_number = models.CharField(max_length=100, blank=False, null=False)
  mission_address = models.CharField(max_length=255, blank=False, null=False)
  postal_code = models.CharField(max_length=20, blank=False, null=False)
  through_swish_or_telephone = models.BooleanField(default=True)
  status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES, default='open')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def clean(self):
    super().clean()
    if not self.category and not self.custom_category:
      raise ValidationError("You must provide either a category or an odd category.")

  def __str__(self):
    return self.heading

  class Meta:
    ordering = ['created_at']
    verbose_name_plural = 'jobs'


class SiteImage(models.Model):
  job=models.ForeignKey('Job', on_delete=models.CASCADE, related_name='images')
  image = models.ImageField(upload_to="uploads/site_images", null=False, blank=False)
  def __str__(self):
    return self.job.heading
  class Meta:
    verbose_name_plural = 'site images'

class Area(models.Model):
  name=models.CharField(max_length=100, unique=True, db_index=True)
  def __str__(self):
    return self.name
  class Meta:
    ordering=['name']
    verbose_name_plural='Areas'
RATING_CHOICES=[
  (1,1),
  (2,2),
  (3,3),
  (4,4),
  (5,5),
]
class Review(models.Model):
  service_provider = models.ForeignKey(
    'accounts.User',
    on_delete=models.CASCADE,
    related_name='reviews_received'  # Company gets reviewed
  )
  user = models.ForeignKey(
    'accounts.User',
    on_delete=models.SET_NULL,
    null=True,
    related_name='reviews_given'  # Private user gives review
  )
  review = models.TextField(blank=False, null=False)
  rating = models.IntegerField(choices=RATING_CHOICES, blank=False, null=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Review for {self.service_provider.email} by {self.user.email}"

  class Meta:
    verbose_name_plural = 'Reviews'

REASON_CHOICES = (("Job is postponed", 'Job is postponed'),
                       ('Found a business outside swish.ma', 'Found a business outside swish.ma'),
                       ('Job is cancelled', 'Job is cancelled'),
                       ('Mistaken post', 'Mistaken post'),
                       ('Budget or requirements changed', 'Budget or requirements changed'),
                       ('Other','Other'))

class JobPauseReason(models.Model):
  job=models.OneToOneField(Job, on_delete=models.CASCADE)
  reasons = MultiSelectField(choices=REASON_CHOICES, blank=False, null=False)

  def __str__(self):
    return f'Pause Reason for {self.job}'
  class Meta:
    verbose_name_plural = 'Pause Reasons'
    ordering = ['job']