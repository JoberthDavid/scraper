import django_filters

from core.models import (
    EquipmentItem,
    WorkmanItem,
    MaterialItem,
    AuxiliaryActivityItem,
    TransportItem,
)


class CompositionCodeFilterMixin:
    """
    Adiciona filtros por código de composição e data-base.
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


class EquipmentCalculationFilter(
    CompositionCodeFilterMixin,
    django_filters.FilterSet,
):
    class Meta:
        model = EquipmentItem
        fields = []


class WorkmanCalculationFilter(
    CompositionCodeFilterMixin,
    django_filters.FilterSet,
):
    class Meta:
        model = WorkmanItem
        fields = []


class MaterialCalculationFilter(
    CompositionCodeFilterMixin,
    django_filters.FilterSet,
):
    class Meta:
        model = MaterialItem
        fields = []


class ActivityCalculationFilter(
    CompositionCodeFilterMixin,
    django_filters.FilterSet,
):
    class Meta:
        model = AuxiliaryActivityItem
        fields = []


class TransportCalculationFilter(
    CompositionCodeFilterMixin,
    django_filters.FilterSet,
):
    class Meta:
        model = TransportItem
        fields = []