import os
import django
import random
from faker import Faker
from django.core.exceptions import ValidationError

# Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swish.settings')
django.setup()

from accounts.models import User
from jobs.models import Review  # Adjust path if your model is in another app

fake = Faker()

def create_fake_reviews(n=100):
  private_users = list(User.objects.filter(role='private'))
  company_users = list(User.objects.filter(role='company'))

  if not private_users or not company_users:
    print("❌ Not enough users to create reviews. Make sure both 'private' and 'company' users exist.")
    return

  reviews_to_create = []

  for _ in range(n):
    reviewer = random.choice(private_users)
    company = random.choice(company_users)
    review_text = fake.paragraph(nb_sentences=3)
    rating = random.randint(1, 5)

    review = Review(
      service_provider=company,
      user=reviewer,
      review=review_text,
      rating=rating
    )

    try:
      review.full_clean()
      reviews_to_create.append(review)
    except ValidationError as e:
      print(f"❌ Skipping invalid review: {e}")

  Review.objects.bulk_create(reviews_to_create)
  print(f"✅ Created {len(reviews_to_create)} reviews.")

if __name__ == "__main__":
  create_fake_reviews(500)
