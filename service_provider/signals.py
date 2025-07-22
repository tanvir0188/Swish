from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import CompanyProfile
import random
import string

def generate_random_password(length=10):
  characters = string.ascii_letters + string.digits
  return ''.join(random.choice(characters) for _ in range(length))

@receiver(post_save, sender=CompanyProfile)
def create_user_for_company(sender, instance, created, **kwargs):
  if created:
    # You can customize this
    password = generate_random_password()

    User.objects.create_user(
      email=instance.business_email,
      first_name=instance.company_name,  # Optional: or leave blank
      last_name="",                      # Optional: company might not have last name
      telephone=instance.phone_number,
      password=password
    )
