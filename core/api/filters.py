import django_filters
from core.models import GenericItem


class GenericItemFilter(django_filters.FilterSet):

    code = django_filters.CharFilter(lookup_expr='startswith')
    genericdescription = django_filters.CharFilter(lookup_expr='description__startswith')
    unit = django_filters.CharFilter(lookup_expr='unit__startswith')
    source_files = django_filters.DateFilter(lookup_expr='data_base__exact')

    class Meta:
        model = GenericItem
        fields = ['code','genericdescription','unit','source_files']