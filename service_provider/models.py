from django.db import models

from accounts.models import User
from jobs.models import Category, Job
# Create your models here.
class CompanyProfile(models.Model):
  clip_balance = models.IntegerField(default=100, blank=False, null=False)
  company_name=models.CharField(max_length=100, unique=True)
  phone_number= models.CharField(max_length=20, unique=True)
  business_email= models.EmailField(unique=True)
  location=models.CharField(max_length=255)
  sub_category=models.ManyToManyField('SubCategory')
  logo=models.ImageField(upload_to='uploads/company_logo', null=True, blank=True)
  wallpaper=models.ImageField(upload_to='uploads/company_wallpaper', null=True, blank=True)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.company_name
  class Meta:
    ordering=['name']
    verbose_name_plural='Companies'

class Employee(models.Model):
  name=models.CharField(max_length=255, blank=False, null=False)
  designation=models.CharField(max_length=255, blank=False, null=False)
  image=models.ImageField(upload_to='uploads/employee_image', null=True, blank=True)
  company=models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
  reference=models.CharField(max_length=255, blank=True, null=True)
  def __str__(self):
    return self.name
  class Meta:
    ordering=['position']
    verbose_name_plural='Employees'

class ClipsAccount(models.Model):
    """
    Represents the Connects balance for a specific user (freelancer).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='connects_account',
        help_text="The user (freelancer) associated with this Connects account."
    )
    balance = models.IntegerField(
        default=100,
        help_text="Current number of Connects available to the user."
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update to the balance."
    )

    class Meta:
        verbose_name = "Connects Account"
        verbose_name_plural = "Connects Accounts"

    def __str__(self):
        return f"{self.user.username}'s Connects: {self.balance}"

    # def add_connects(self, amount, transaction_type, source_object=None, description=""):
    #     """
    #     Adds Connects to the account and records the transaction.
    #     """
    #     if amount <= 0:
    #         raise ValueError("Amount to add must be positive.")
    #
    #     self.balance += amount
    #     self.save()
    #
    #     ConnectsTransaction.objects.create(
    #         account=self,
    #         amount=amount,
    #         transaction_type=transaction_type,
    #         change_type=ConnectsTransaction.CHANGE_TYPE_ADD,
    #         source_object_id=source_object.pk if source_object else None,
    #         source_content_type=models.ContentType.objects.get_for_model(source_object) if source_object else None,
    #         description=description
    #     )
    #     return self.balance
    #
    # def subtract_connects(self, amount, transaction_type, target_object=None, description=""):
    #     """
    #     Subtracts Connects from the account and records the transaction.
    #     Raises ValueError if not enough Connects are available.
    #     """
    #     if amount <= 0:
    #         raise ValueError("Amount to subtract must be positive.")
    #     if self.balance < amount:
    #         raise ValueError("Insufficient Connects.")
    #
    #     self.balance -= amount
    #     self.save()
    #
    #     ConnectsTransaction.objects.create(
    #         account=self,
    #         amount=amount,
    #         transaction_type=transaction_type,
    #         change_type=ConnectsTransaction.CHANGE_TYPE_SUBTRACT,
    #         target_object_id=target_object.pk if target_object else None,
    #         target_content_type=models.ContentType.objects.get_for_model(target_object) if target_object else None,
    #         description=description
    #     )
    #     return self.balance


