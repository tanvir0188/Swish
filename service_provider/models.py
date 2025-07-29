from datetime import timedelta

from django.db import models
from multiselectfield import MultiSelectField

from accounts.models import User
from jobs.models import Category, Job, SubCategory
# Create your models here.
class CompanyProfile(models.Model):
  user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
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
  status=models.CharField(max_length=10, choices=BID_STATUS_CHOICES, null=True, blank=True)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  def __str__(self):
    return f'{self.job.heading}-{self.bidding_company}'
  class Meta:
    unique_together=('job', 'bidding_company')

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

PACKAGE_CHOICES = [
  ('Starter', 'Starter'),
  ('Growth', 'Growth'),
  ('Pro', 'Pro'),
  ('Elite', 'Elite')
]

class TokenPackage(models.Model):
  company=models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
  is_paid=models.BooleanField(default=True)
  package_name=models.CharField(choices=PACKAGE_CHOICES, blank=False, null=False)
  package_balance=models.PositiveIntegerField(blank=False, null=False)
  issued_at=models.DateTimeField(auto_now_add=True)
  expires_at=models.DateTimeField(blank=False, null=False)

  def save(self, *args, **kwargs):
    if self.package_name == 'Starter' and not self.is_paid:
      self.package_balance = 40
      self.expires_at = self.issued_at + timedelta(days=90)
    elif self.package_name == 'Starter' and self.is_paid:
      self.package_balance=40
      self.expires_at=self.issued_at+timedelta(days=365)
    elif self.package_name == 'Growth':
      self.package_balance = 100
      self.expires_at = self.issued_at + timedelta(days=365)
    elif self.package_name == 'Pro':
      self.package_balance = 200
      self.expires_at = self.issued_at + timedelta(days=365)
    elif self.package_name == 'Elite':
      self.package_balance = 400
      self.expires_at = self.issued_at + timedelta(days=365)

    super().save(*args, **kwargs)


#Token transaction is actually the token
class TokenTransaction(models.Model):
  package=models.ForeignKey(TokenPackage, on_delete=models.CASCADE)
  job=models.OneToOneField(Job, on_delete=models.SET_NULL,null=True, related_name='transactions')
  used_by=models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name='transactions')
  used_at=models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.job.heading} - {self.used_by.email}"
  class Meta:
    unique_together=('job', 'used_by')


