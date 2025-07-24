from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile
from service_provider.models import CompanyProfile

@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
  if created:
    if instance.role == 'company':
      CompanyProfile.objects.create(user=instance)
    elif instance.role == 'private':
      Profile.objects.create(user=instance)
