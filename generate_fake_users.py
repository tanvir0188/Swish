import os
import django
import random
from faker import Faker
from django.core.exceptions import ValidationError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swish.settings')  # Change if needed
django.setup()

from accounts.models import User

fake = Faker()

def create_users(n=30):
  roles = ['private', 'company']
  users_to_create = []

  for _ in range(n):
    role = random.choice(roles)
    first_name = fake.first_name()
    surname = fake.last_name()
    email = fake.unique.email()
    telephone = fake.phone_number()
    city = fake.city()
    home_address = fake.address()
    language = fake.language_name()

    user = User(
      first_name=first_name,
      surname=surname,
      full_name=f"{first_name} {surname}",
      email=email,
      telephone=telephone,
      role=role,
      city=city,
      home_address=home_address,
      language=language,
    )
    user.set_password('password123')  # Set a default password

    try:
      user.full_clean()
      users_to_create.append(user)
    except ValidationError as e:
      print(f"❌ Skipping invalid user: {e}")

  User.objects.bulk_create(users_to_create)
  print(f"✅ Created {len(users_to_create)} users.")

if __name__ == "__main__":
  create_users(30)
