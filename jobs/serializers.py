from rest_framework import serializers

from jobs.models import Job, Category, SubCategory


class JobSerializer(serializers.ModelSerializer):
  class Meta:
    model = Job
    fields=['heading', 'description','category', 'estimated_time', 'estimated_employees', 'value', 'email', 'first_name', 'last_name', 'telephone', 'mission_address', 'postal_code', 'contact_swish']

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
