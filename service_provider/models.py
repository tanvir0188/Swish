from datetime import timedelta
from django.utils.timezone import localtime

from django.utils import timezone
from django.db import models
from multiselectfield import MultiSelectField

from accounts.models import User
from jobs.models import Category, Job, SubCategory, Area


# Create your models here.
class CompanyProfile(models.Model):
  user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
  company_name=models.CharField(max_length=100, unique=True)
  phone_number= models.CharField(max_length=20, unique=True)
  sub_category=models.ManyToManyField(SubCategory, blank=True)
  area = models.ManyToManyField(Area, blank=True)
  logo=models.ImageField(upload_to='uploads/company_logos', null=True, blank=True)
  wallpaper=models.ImageField(upload_to='uploads/company_wallpapers', null=True, blank=True)
  about=models.TextField(blank=True, null=True)
  ice_number=models.CharField(max_length=255, unique=True)
  business_email=models.CharField(max_length=255, unique=True)
  address=models.TextField(blank=True, null=True)
  city=models.CharField(max_length=255, blank=True, null=True)
  opening_hours = models.JSONField(blank=True, null=True, default=dict)
  homepage=models.URLField(blank=True)
  facebook=models.URLField(blank=True)
  instagram=models.URLField(blank=True)
  youtube=models.URLField(blank=True)
  tiktok=models.URLField(blank=True)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  open_in_weekend=models.BooleanField(default=False)

  def __str__(self):
    return self.company_name
  class Meta:
    ordering=['company_name']
    verbose_name_plural='Companies'
    verbose_name='Company'

BID_STATUS_CHOICES = [
  ('Active', 'Active'),
  ('Complete', 'Complete'),
  ('Rejected', 'Rejected'),
]
class Bid(models.Model):
  job=models.ForeignKey(Job, on_delete=models.CASCADE)
  bidding_company=models.ForeignKey('accounts.User',on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
  time_estimate=models.CharField(max_length=100,blank=False, null=False)
  proposal_description=models.TextField(blank=False, null=False, max_length=500)
  status=models.CharField(max_length=10, choices=BID_STATUS_CHOICES, null=True, blank=True, default='Active')
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  def __str__(self):
    return f'{self.job.heading}-{self.bidding_company}'
  class Meta:
    unique_together=('job', 'bidding_company')

class Employee(models.Model):
  first_name=models.CharField(max_length=255, blank=False, null=False)
  last_name = models.CharField(max_length=255, blank=False, null=False)
  role=models.CharField(max_length=255, blank=False, null=False)
  image=models.ImageField(upload_to='uploads/employee_images', null=True, blank=True)
  phone_number=models.CharField(blank=True, null=True)
  company=models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
  reference=models.CharField(max_length=255, blank=True, null=True)
  email=models.EmailField(blank=False, null=False)
  def __str__(self):
    return f'{self.first_name} {self.last_name}'
  class Meta:
    ordering=['role']
    verbose_name_plural='Employees'

PACKAGE_CHOICES = [
  ('Starter', 'Starter'),
  ('Growth', 'Growth'),
  ('Pro', 'Pro'),
  ('Elite', 'Elite')
]

class TokenPackage(models.Model):
  company=models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_packages')
  is_paid=models.BooleanField(default=True)
  package_name=models.CharField(choices=PACKAGE_CHOICES, blank=False, null=False)
  package_balance=models.PositiveIntegerField(blank=False, null=False)
  issued_at=models.DateTimeField(auto_now_add=True)
  expires_at=models.DateTimeField(blank=False, null=False)
  is_partner=models.BooleanField(default=False, blank=False, null=False)

  def save(self, *args, **kwargs):
    now = timezone.now()
    if self._state.adding:
      if self.package_name == 'Starter' and not self.is_paid:
        self.package_balance = 40
        self.expires_at = now + timedelta(days=90)
      elif self.package_name == 'Starter' and self.is_paid:
        self.package_balance=40
        self.expires_at=now+timedelta(days=365)
      elif self.package_name == 'Growth':
        self.package_balance = 100
        self.expires_at = now + timedelta(days=365)
      elif self.package_name == 'Pro':
        self.package_balance = 200
        self.expires_at = now + timedelta(days=365)
      elif self.package_name == 'Elite':
        self.package_balance = 400
        self.expires_at = now + timedelta(days=365)

    super().save(*args, **kwargs)
  def __str__(self):
    return self.package_name
#Token transaction is actually the token
class TokenTransaction(models.Model):
  package=models.ForeignKey(TokenPackage, on_delete=models.CASCADE, related_name='transactions')
  job=models.OneToOneField(Job, on_delete=models.SET_NULL,null=True, related_name='token_transaction')
  used_by=models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name='token_transactions')
  used_at=models.DateTimeField(auto_now_add=True)

  def __str__(self):
    formatted_time = localtime(self.used_at).strftime('%b %d, %Y – %I:%M %p')
    return f"{self.job.heading} - {self.used_by.company_profile.company_name} used at {formatted_time}"
  class Meta:
    unique_together=('job', 'used_by')

# class Certification(models.Model):
#   company=models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
#   certifications=models.FileField(upload_to='uploads/certification', null=True, blank=True)
#   def __str__(self):
#     re

