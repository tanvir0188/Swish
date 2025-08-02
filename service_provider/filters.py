# jobs/filters.py
import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
  min_value = django_filters.NumberFilter(field_name="value", lookup_expr='gte')
  max_value = django_filters.NumberFilter(field_name="value", lookup_expr='lte')
  subcategory = django_filters.CharFilter(field_name="category__sub_categories__name", lookup_expr='iexact')
  area = django_filters.CharFilter(field_name="area__name", lookup_expr='iexact')

  class Meta:
    model = Job
    fields = ['min_value', 'max_value', 'subcategory', 'area']
