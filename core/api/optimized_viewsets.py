from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.api.viewsets import ReadOnly
from core.models import (
    Composition,
    EquipmentItem,
    WorkmanItem,
    MaterialItem,
    AuxiliaryActivityItem,
    TransportItem,
)

from core.api.optimized_filters import (
    EquipmentCalculationFilter,
    WorkmanCalculationFilter,
    MaterialCalculationFilter,
    ActivityCalculationFilter,
    TransportCalculationFilter,
)

from core.api.optimized_serializers import (
    CompositionStructureActivitySerializer,
    EquipmentCalculationSerializer,
    WorkmanCalculationSerializer,
    MaterialCalculationSerializer,
    TransportCalculationSerializer,
)


class OptimizedReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    ViewSet base para endpoints otimizados somente leitura.
    """

    http_method_names = ["get"]
    permission_classes = [ReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]


class CompositionActivityViewSet(
    OptimizedReadOnlyViewSet
):
    serializer_class = CompositionStructureActivitySerializer
    filterset_class = ActivityCalculationFilter

    ordering_fields = [
        "composition__generic_item__code",
        "generic_item__code",
    ]

    ordering = [
        "composition__generic_item__code",
        "id",
    ]

    def get_queryset(self):
        return (
            AuxiliaryActivityItem.objects
            .select_related(
                "composition",
                "composition__generic_item",
                "generic_item",
            )
            .only(
                "id",
                "composition_id",
                "generic_item_id",
                "input_quantity",
                "composition__generic_item__code",
                "generic_item__code",
            )
        )


class EquipmentCalculationViewSet(
    OptimizedReadOnlyViewSet
):
    serializer_class = EquipmentCalculationSerializer
    filterset_class = EquipmentCalculationFilter

    ordering_fields = [
        "composition__generic_item__code",
        "generic_item__code",
    ]

    ordering = [
        "composition__generic_item__code",
        "id",
    ]

    def get_queryset(self):
        return (
            EquipmentItem.objects
            .select_related(
                "composition",
                "composition__generic_item",
                "generic_item",
                "unit",
            )
            .only(
                "id",
                "composition_id",
                "generic_item_id",
                "unit_id",
                "input_group",
                "input_quantity",
                "input_use",
                "composition__generic_item__code",
                "generic_item__code",
                "unit__unit",
            )
        )


class WorkmanCalculationViewSet(
    OptimizedReadOnlyViewSet
):
    serializer_class = WorkmanCalculationSerializer
    filterset_class = WorkmanCalculationFilter

    ordering_fields = [
        "composition__generic_item__code",
        "generic_item__code",
    ]

    ordering = [
        "composition__generic_item__code",
        "id",
    ]

    def get_queryset(self):
        return (
            WorkmanItem.objects
            .select_related(
                "composition",
                "composition__generic_item",
                "generic_item",
                "unit",
            )
            .only(
                "id",
                "composition_id",
                "generic_item_id",
                "unit_id",
                "input_group",
                "input_quantity",
                "composition__generic_item__code",
                "generic_item__code",
                "unit__unit",
            )
        )


class MaterialCalculationViewSet(
    OptimizedReadOnlyViewSet
):
    serializer_class = MaterialCalculationSerializer
    filterset_class = MaterialCalculationFilter

    ordering_fields = [
        "composition__generic_item__code",
        "generic_item__code",
    ]

    ordering = [
        "composition__generic_item__code",
        "id",
    ]

    def get_queryset(self):
        return (
            MaterialItem.objects
            .select_related(
                "composition",
                "composition__generic_item",
                "generic_item",
                "unit",
            )
            .only(
                "id",
                "composition_id",
                "generic_item_id",
                "unit_id",
                "input_group",
                "input_quantity",
                "composition__generic_item__code",
                "generic_item__code",
                "unit__unit",
            )
        )


class TransportCalculationViewSet(
    OptimizedReadOnlyViewSet
):
    serializer_class = TransportCalculationSerializer
    filterset_class = TransportCalculationFilter

    ordering_fields = [
        "composition__generic_item__code",
        "generic_item__code",
    ]

    ordering = [
        "composition__generic_item__code",
        "id",
    ]

    def get_queryset(self):
        return (
            TransportItem.objects
            .select_related(
                "composition",
                "composition__generic_item",
                "generic_item",
                "unit",
                "proprietary_item",
            )
            .only(
                "id",
                "composition_id",
                "generic_item_id",
                "unit_id",
                "proprietary_item_id",
                "input_group",
                "input_quantity",
                "composition__generic_item__code",
                "generic_item__code",
                "unit__unit",
                "proprietary_item__code",
            )
        )