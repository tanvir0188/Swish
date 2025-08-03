import os
import django
import random
from faker import Faker
from django.core.exceptions import ValidationError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swish.settings')  # Change if needed
django.setup()

from jobs.models import Job, Category, CustomCategory, Area
from accounts.models import User

fake = Faker()

def create_jobs(n=1000):
  private_users = User.objects.filter(role='private')
  categories = Category.objects.all()
  areas = Area.objects.all()

  if not private_users.exists():
    print("❌ No private users found.")
    return
  if not categories.exists():
    print("❌ No categories found.")
    return
  if not areas.exists():
    print("❌ No areas found.")
    return

  jobs_to_create = []

  for _ in range(n):
    user = random.choice(private_users)
    category = random.choice(categories)
    area = random.choice(areas)

    job = Job(
      posted_by=user,
      heading=fake.sentence(nb_words=6),
      description=fake.paragraph(nb_sentences=5),
      estimated_time=f"{random.randint(1, 12)} weeks",
      employee_need=random.randint(1, 10),
      area=area,
      value=round(random.uniform(1000, 50000), 2),
      category=category,  # You can alternate with custom_category if needed
      email=user.email,
      first_name=user.first_name or fake.first_name(),
      surname=user.surname or fake.last_name(),
      telephone_number=user.telephone or fake.phone_number(),
      mission_address=fake.address(),
      postal_code=fake.postcode(),
      through_swish_or_telephone=random.choice([True, False]),
      status='Open',
    )

    try:
      job.full_clean()  # Run model validation
      jobs_to_create.append(job)
    except ValidationError as e:
      print(f"❌ Skipping invalid job: {e}")

  Job.objects.bulk_create(jobs_to_create)
  print(f"✅ Created {len(jobs_to_create)} jobs.")

if __name__ == "__main__":
  create_jobs(1000)
