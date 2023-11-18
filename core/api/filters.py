import django_filters
from core.models import SourceFile, GenericItem, GenericDescription, MonetaryValue, Composition


class SourceFileFilter(django_filters.FilterSet):

    class Meta:
        model = SourceFile
        fields = {'data_base':['year__gte'],
                  'methodology':['startswith'],
                  'uf':['startswith','in'],
                  'type_system':['startswith'],
                  'type_file':['startswith'],
                  }


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


class MonetaryValueFilter(django_filters.FilterSet):

    classification = django_filters.CharFilter(lookup_expr='startswith')
    group = django_filters.CharFilter(lookup_expr='startswith')
    generic_item = django_filters.CharFilter(lookup_expr='code__startswith')
    unit = django_filters.CharFilter(lookup_expr='unit__startswith')

    class Meta:
        model = MonetaryValue
        fields = ['classification', 'group', 'generic_item', 'unit']


class CompositionFilter(django_filters.FilterSet):

    class Meta:
        model = Composition
        fields = { 'source_file__data_base':['exact'],
                  'composition_group':['startswith','in'],
                  'generic_item__code':['exact','in'],
                  'generic_description__description':['startswith'],
                  }    