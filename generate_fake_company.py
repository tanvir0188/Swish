import os
import django
import random
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swish.settings')  # Change if needed
django.setup()

from accounts.models import User
from service_provider.models import CompanyProfile
from jobs.models import SubCategory, Area

fake = Faker()

def create_fake_company_profiles(n=15):
    # Get users without company profiles
    users_without_company = User.objects.filter(role='company').exclude(company_profile__isnull=False)
    if users_without_company.count() < n:
        print(f"⚠️ Only {users_without_company.count()} users without company profile available.")
        n = users_without_company.count()

    subcategories = list(SubCategory.objects.all())
    areas = list(Area.objects.all())

    created = 0

    for user in random.sample(list(users_without_company), n):
        company_name = fake.company()
        phone_number = fake.phone_number()
        ice_number = fake.bothify(text='??######')  # e.g. AB123456
        business_email = fake.company_email()

        company_profile = CompanyProfile(
            user=user,
            company_name=company_name,
            phone_number=phone_number,
            ice_number=ice_number,
            business_email=business_email,
            about=fake.text(max_nb_chars=200),
            address=fake.address(),
            city=fake.city(),
            monday_time=None,
            tuesday_time=None,
            wednesday_time=None,
            thursday_time=None,
            friday_time=None,
            saturday_time=None,
            sunday_time=None,
            homepage=fake.url(),
            facebook=f'https://facebook.com/{fake.user_name()}',
            instagram=f'https://instagram.com/{fake.user_name()}',
            youtube=f'https://youtube.com/{fake.user_name()}',
            tiktok=f'https://tiktok.com/@{fake.user_name()}',
            open_in_weekend=fake.boolean(chance_of_getting_true=20),
        )

        try:
            company_profile.save()

            # Add random subcategories and areas (optional)
            if subcategories:
                company_profile.sub_category.set(random.sample(subcategories, k=min(3, len(subcategories))))
            if areas:
                company_profile.area.set(random.sample(areas, k=min(3, len(areas))))

            company_profile.save()
            created += 1
            print(f"✅ Created company profile for user: {user.email} - {company_name}")
        except Exception as e:
            print(f"❌ Failed to create for user {user.email}: {e}")

    print(f"\n✅ Total company profiles created: {created}")

if __name__ == "__main__":
    create_fake_company_profiles(15)
