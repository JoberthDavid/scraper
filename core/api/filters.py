import django_filters
from core.models import GenericItem, GenericDescription, Composition


class GenericItemFilter(django_filters.FilterSet):

    source_files = django_filters.DateFilter(lookup_expr='data_base__exact')
    group = django_filters.CharFilter(lookup_expr='startswith')
    code = django_filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = GenericItem
        fields = ['source_files', 'group', 'code',]


class GenericDescriptionFilter(django_filters.FilterSet):

    source_files = django_filters.DateFilter(lookup_expr='data_base__exact')
    group = django_filters.CharFilter(lookup_expr='startswith')
    generic_item = django_filters.CharFilter(lookup_expr='code__startswith')
    description = django_filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = GenericDescription
        fields = ['source_files', 'group', 'generic_item', 'description']


class CompositionFilter(django_filters.FilterSet):

    source_file = django_filters.DateFilter(lookup_expr='data_base__exact')
    composition_group = django_filters.CharFilter(lookup_expr='startswith')
    generic_item = django_filters.CharFilter(lookup_expr='code__startswith')
    generic_description = django_filters.CharFilter(lookup_expr='description__startswith')

    class Meta:
        model = Composition
        fields = ['source_file', 'composition_group', 'generic_item', 'generic_description']