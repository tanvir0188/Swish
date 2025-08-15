import os
import django
import random
from faker import Faker
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swish.settings')
django.setup()

from accounts.models import User
from service_provider.models import TokenPackage, TokenTransaction
from jobs.models import Job

fake = Faker()
NUM_TRANSACTIONS = 500

# Eligible companies and jobs
companies = User.objects.filter(role='company', company_profile__isnull=False)
jobs = list(Job.objects.all())  # convert to list for random.choice

if not companies.exists() or not jobs:
    print("❌ No eligible companies or jobs found.")
    exit()

def get_earliest_package(company):
    """Return earliest valid package (FIFO) with available balance, or None."""
    return TokenPackage.objects.filter(
        company=company,
        package_balance__gt=0,
        expires_at__gte=timezone.now()
    ).order_by('issued_at').first()

created_count = 0

# Precompute which jobs each company has unlocked
company_job_map = {
    company.id: set(TokenTransaction.objects.filter(used_by=company).values_list('job_id', flat=True))
    for company in companies
}

for _ in range(NUM_TRANSACTIONS):
    company = random.choice(companies)

    # Skip if no available package (balance) for this company
    package = get_earliest_package(company)
    if not package:
        continue

    # Dynamically get jobs not yet unlocked by this company
    unlocked_job_ids = set(TokenTransaction.objects.filter(used_by=company).values_list('job_id', flat=True))
    available_jobs = [j for j in jobs if j.id not in unlocked_job_ids]

    if not available_jobs:
        continue  # company unlocked all jobs

    job = random.choice(available_jobs)

    # Create transaction
    TokenTransaction.objects.create(
        package=package,
        job=job,
        used_by=company
    )

    # Deduct 1 token
    package.package_balance -= 1
    package.save()

    created_count += 1


print(f"✅ Created {created_count} token transactions.")
