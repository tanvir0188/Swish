import os
from decimal import Decimal, ROUND_DOWN

import django
import random
from faker import Faker
from django.core.exceptions import ValidationError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swish.settings')  # adjust as needed
django.setup()

from jobs.models import Job
from service_provider.models import Bid
from accounts.models import User

fake = Faker()

def create_bids(n=1000):
  # Only company users who have a company_profile
  company_users = User.objects.filter(role='company', company_profile__isnull=False)
  open_jobs = Job.objects.filter(status='Open')

  if not company_users.exists():
    print("❌ No users with role 'company' AND company_profile found.")
    return
  if not open_jobs.exists():
    print("❌ No jobs with status 'Open' found.")
    return

  bids_to_create = []
  created_pairs = set()  # track (job_id, user_id) to avoid duplicates

  # preload existing bids to skip duplicates efficiently
  existing_bids = set(
    Bid.objects.filter(
      job__in=open_jobs,
      bidding_company__in=company_users
    ).values_list('job_id', 'bidding_company_id')
  )
  created_pairs.update(existing_bids)

  attempts = 0
  max_attempts = n * 3  # avoid infinite loop in case of limited combos

  while len(bids_to_create) < n and attempts < max_attempts:
    job = random.choice(open_jobs)
    user = random.choice(company_users)
    key = (job.id, user.id)
    amount = Decimal(str(random.uniform(100, 50000))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    if key in created_pairs:
      attempts += 1
      continue

    bid = Bid(
      job=job,
      bidding_company=user,
      amount=amount,
      time_estimate=f"{random.randint(1, 30)} days",
      proposal_description=fake.text(max_nb_chars=200),
      status='Active',
    )
    try:
      bid.full_clean()
      bids_to_create.append(bid)
      created_pairs.add(key)
    except ValidationError as e:
      print(f"❌ Skipping invalid bid: {e}")
    attempts += 1

  Bid.objects.bulk_create(bids_to_create)
  print(f"✅ Created {len(bids_to_create)} bids.")

if __name__ == "__main__":
  create_bids(1000)
