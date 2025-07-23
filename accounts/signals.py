from django.db.models.signals import post_save
from django.dispatch import receiver

from service_provider.models import CompanyProfile
from .models import User, Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  """Create a Profile instance when a normal (non-company) user is created."""
  if created:
    is_company_email = CompanyProfile.objects.filter(business_email=instance.email).exists()
    if not is_company_email:
      Profile.objects.create(
        user=instance,
        first_name=instance.first_name,
        last_name=instance.last_name,
      )
