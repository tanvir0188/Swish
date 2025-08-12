from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from jobs.models import SubCategory


# Create your models here.


class CustomUserManager(BaseUserManager):
  def _create_user(self, email, first_name, surname, telephone, password, **extra_fields):
    if not email:
      raise ValueError('Users must have an email address')

    email = self.normalize_email(email)
    user = self.model(email=email, first_name=first_name,surname=surname, telephone=telephone,  **extra_fields)

    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, first_name, surname, telephone, password, **extra_fields):
    extra_fields.setdefault('is_superuser', False)
    return self._create_user(email, first_name, surname, telephone, password, **extra_fields)

  def create_superuser(self, email, first_name, surname, telephone, password, **extra_fields):
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('is_staff', True)

    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self._create_user(email, first_name, surname, telephone, password, **extra_fields)
ROLE_CHOICES = [
  ('private', 'Private'),
  ('company', 'Company'),
]
class User(AbstractUser):
  username=None
  first_name = models.CharField(max_length=255, blank=True, null=True)
  surname = models.CharField(max_length=255, blank=True, null=True)
  full_name=models.CharField(max_length=255, blank=True, null=True)
  telephone= models.CharField(max_length=255, blank=True, null=True)
  role=models.CharField(choices=ROLE_CHOICES, max_length=255, blank=False, null=False)
  city=models.CharField(max_length=255, blank=True, null=True)
  home_address=models.CharField(max_length=255, blank=True, null=True)
  email = models.EmailField(unique=True)
  otp = models.CharField(max_length=4, blank=True, null=True)
  otp_expires = models.DateTimeField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  language=models.CharField(max_length=255, blank=True, null=True)
  image = models.ImageField(upload_to='uploads/profile_images/', blank=True, null=True)
  last_seen = models.DateTimeField(null=True, blank=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name','surname', 'telephone']

  objects = CustomUserManager()

  def __str__(self):
    return f'{self.first_name} {self.surname}'

  def save(self, *args, **kwargs):
    self.full_name = f'{self.first_name or ""} {self.surname or ""}'.strip()
    super().save(*args, **kwargs)

  class Meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'

class PreSubscription(models.Model):
  company_name=models.CharField(max_length=255, null=True, blank=True)
  full_name=models.CharField(max_length=255, null=True, blank=True)
  email=models.EmailField(max_length=255, null=False, blank=False, unique=True)
  role = models.CharField(choices=ROLE_CHOICES, max_length=255, null=False, blank=False)
  city=models.CharField(max_length=255, null=True, blank=True)
  phone_number=models.CharField(max_length=255, null=True, blank=True)
  ice_number=models.CharField(max_length=255, null=True, blank=True)
  def __str__(self):
    return f'{self.email}'
  class Meta:
    verbose_name = 'Pre Subscription'
    verbose_name_plural = 'PreSubscription Before Launching'

class Feedback(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  suggestion=models.TextField(blank=False, null=False)
  def __str__(self):
    return f'Feedback({self.user.email})'
  class Meta:
    verbose_name = 'Feedback'
    verbose_name_plural = 'Feedbacks'
