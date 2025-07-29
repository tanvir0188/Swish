from rest_framework import serializers, fields

from jobs.models import Job, Category, SubCategory, Review, JobPauseReason, REASON_CHOICES
from service_provider.models import Bid


class JobSerializer(serializers.ModelSerializer):
  class Meta:
    model = Job
    fields=['heading', 'description','category', 'estimated_time', 'employee_need','site_photo', 'value', 'email', 'first_name', 'surname', 'telephone_number', 'mission_address', 'postal_code', 'through_swish_or_telephone']

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
