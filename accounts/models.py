from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.


class CustomUserManager(BaseUserManager):
  def _create_user(self, email, first_name, last_name, telephone, password, **extra_fields):
    if not email:
      raise ValueError('Users must have an email address')

    email = self.normalize_email(email)
    user = self.model(email=email, first_name=first_name,last_name=last_name, telephone=telephone,  **extra_fields)

    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, first_name, last_name, telephone, password, **extra_fields):
    extra_fields.setdefault('is_superuser', False)
    return self._create_user(email, first_name, last_name, telephone, password, **extra_fields)

  def create_superuser(self, email, first_name, last_name, telephone, password, **extra_fields):
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('is_staff', True)

    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self._create_user(email, first_name, last_name, telephone, password, **extra_fields)

class User(AbstractUser):
  username=None
  first_name = models.CharField(max_length=255, blank=True, null=True)
  last_name = models.CharField(max_length=255, blank=True, null=True)
  telephone= models.CharField(max_length=255, blank=True, null=True)
  email = models.EmailField(unique=True)
  otp = models.CharField(max_length=4, blank=True, null=True)
  otp_expires = models.DateTimeField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name','last_name', 'telephone']

  objects = CustomUserManager()

  def __str__(self):
    return self.first_name


  class Meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'



class Profile(models.Model):
  user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='profile')
  bio = models.TextField(blank=True, null=True)
  image = models.ImageField(upload_to='uploads/profile_images/', blank=True, null=True)
  full_name = models.CharField(max_length=255, blank=True, null=True)

  def __str__(self):
    return f'{self.user or self.user.email}'

  class Meta:
    verbose_name = 'profile'
    verbose_name_plural = 'profiles'


	