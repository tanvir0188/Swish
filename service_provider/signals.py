from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import CompanyProfile, TokenPackage

@receiver(post_save, sender=User)
def create_company_profile(sender, instance, created, **kwargs):
  if created and instance.role == 'company':
    # Create a CompanyProfile linked to the new user
    CompanyProfile.objects.create(user=instance,company_name=instance.company_name, phone_number=instance.telephone)
    TokenPackage.objects.create(company=instance,is_paid = False, package_name='Starter')