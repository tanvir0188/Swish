from django.db import models

from accounts.models import User
from jobs.models import Category, Job, SubCategory
# Create your models here.
class CompanyProfile(models.Model):
  user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
  clip_balance = models.IntegerField(default=100, blank=False, null=False)
  clip_granted_at=models.DateTimeField(auto_now_add=True)
  company_name=models.CharField(max_length=100, unique=True)
  phone_number= models.CharField(max_length=20, unique=True)
  sub_category=models.ManyToManyField(SubCategory, blank=True)
  logo=models.ImageField(upload_to='uploads/company_logos', null=True, blank=True)
  wallpaper=models.ImageField(upload_to='uploads/company_wallpapers', null=True, blank=True)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.company_name
  class Meta:
    ordering=['company_name']
    verbose_name_plural='Companies'
    verbose_name='Company'

class Employee(models.Model):
  name=models.CharField(max_length=255, blank=False, null=False)
  designation=models.CharField(max_length=255, blank=False, null=False)
  image=models.ImageField(upload_to='uploads/employee_images', null=True, blank=True)
  company=models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
  reference=models.CharField(max_length=255, blank=True, null=True)
  def __str__(self):
    return self.name
  class Meta:
    ordering=['designation']
    verbose_name_plural='Employees'

class ClipTransaction(models.Model):
  job=models.OneToOneField(Job, on_delete=models.SET_NULL,null=True, related_name='transaction')
  user=models.OneToOneField(User, on_delete=models.SET_NULL,null=True, related_name='transaction')

  def __str__(self):
    return f"{self.job.heading} - {self.user.email}"
  class Meta:
    unique_together=('job', 'user')


