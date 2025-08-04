from rest_framework import serializers, fields

from jobs.models import Job, Category, SubCategory, Review, JobPauseReason, REASON_CHOICES, SiteImage
from service_provider.models import Bid


class JobSerializer(serializers.ModelSerializer):
  site_images = serializers.ListField(
    child=serializers.ImageField(),
    write_only=True,
    required=False
  )

  class Meta:
    model = Job
    fields = [
      'heading', 'description', 'category', 'custom_category',
      'estimated_time', 'employee_need', 'value', 'email', 'first_name',
      'surname', 'telephone_number', 'mission_address', 'area',
      'postal_code', 'through_swish_or_telephone', 'site_images'
    ]

  def create(self, validated_data):
    # Remove site_images before creating the Job
    site_images = validated_data.pop('site_images', [])
    job = Job.objects.create(**validated_data)

    # Attach images after job is created
    for image in site_images:
      SiteImage.objects.create(job=job, image=image)

    return job


class SitePhotoSerializer(serializers.ModelSerializer):
  class Meta:
    model = SiteImage
    fields = ['image']

class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields='__all__'

class SubCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = SubCategory
    fields=['id', 'name']

class CategoryDetailListSerializer(serializers.ModelSerializer):
  sub_categories=SubCategorySerializer(many=True, read_only=True)
  class Meta:
    model = Category
    fields=['id', 'name', 'category_icon', 'description', 'sub_categories']

class AddSubCategorySerializer(serializers.Serializer):
  category = serializers.IntegerField()
  name = serializers.ListField(
    child=serializers.CharField(),
    allow_empty=False
  )

  def validate_category(self, value):
    if not Category.objects.filter(id=value).exists():
      raise serializers.ValidationError("Category does not exist.")
    return value


class BidStatusUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Bid
    fields = ['status']

class ReviewSerializer(serializers.ModelSerializer):
  class Meta:
    model=Review
    fields=['review', 'rating']

class JobPausingReasonSerializer(serializers.ModelSerializer):
  reasons = serializers.MultipleChoiceField(choices=REASON_CHOICES)
  class Meta:
    model = JobPauseReason
    fields=['reasons']
