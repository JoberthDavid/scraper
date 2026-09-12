import django_filters

from core.models import (
    EquipmentItem,
    WorkmanItem,
    MaterialItem,
    AuxiliaryActivityItem,
    TransportItem,
)


class CompositionCodeFilterSet(django_filters.FilterSet):
    """
    Filtros comuns aos itens vinculados a uma composição.
    """

    composition_code = django_filters.CharFilter(
        field_name="composition__generic_item__code",
        lookup_expr="exact",
    )

    composition_code__in = django_filters.BaseInFilter(
        field_name="composition__generic_item__code",
        lookup_expr="in",
    )

    data_base = django_filters.DateFilter(
        field_name="composition__source_files__data_base",
        lookup_expr="exact",
    )


class EquipmentCalculationFilter(CompositionCodeFilterSet):
    class Meta:
        model = EquipmentItem
        fields = []


class WorkmanCalculationFilter(CompositionCodeFilterSet):
    class Meta:
        model = WorkmanItem
        fields = []


class MaterialCalculationFilter(CompositionCodeFilterSet):
    class Meta:
        model = MaterialItem
        fields = []


class ActivityCalculationFilter(CompositionCodeFilterSet):
    class Meta:
        model = AuxiliaryActivityItem
        fields = []


class TransportCalculationFilter(CompositionCodeFilterSet):
    class Meta:
        model = TransportItem
        fields = []