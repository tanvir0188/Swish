from django_filters import rest_framework as filters

from jobs.models import Job


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
  pass

class JobFilter(filters.FilterSet):
  min_value = filters.NumberFilter(field_name="value", lookup_expr='gte')
  max_value = filters.NumberFilter(field_name="value", lookup_expr='lte')
  subcategory = CharInFilter(field_name="category__sub_categories__name", lookup_expr='in')
  area = CharInFilter(field_name="area__name", lookup_expr='in')

  class Meta:
    model = Job
    fields = ['min_value', 'max_value', 'subcategory', 'area']
