from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CompanyProfile, TokenPackage

@receiver(post_save, sender=CompanyProfile)
def create_token_package(sender, instance, created, **kwargs):
  if created:
    TokenPackage.objects.create(company=instance.user,is_paid = False, package_name='Starter')