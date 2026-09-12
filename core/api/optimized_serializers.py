from rest_framework import serializers

from core.models import (
    Composition,
    EquipmentItem,
    WorkmanItem,
    MaterialItem,
    AuxiliaryActivityItem,
    TransportItem,
)


class CompositionStructureSerializer(serializers.ModelSerializer):
    """
    Serializer mínimo utilizado para descoberta da estrutura
    recursiva das composições.
    """

    generic_item = serializers.CharField(
        source="generic_item.code",
        read_only=True,
    )

    class Meta:
        model = Composition
        fields = [
            "id",
            "composition_group",
            "generic_item",
            "fic",
            "production",
        ]


class CompositionStructureActivitySerializer(
    serializers.ModelSerializer
):
    """
    Serializer mínimo das atividades auxiliares.

    Somente os campos necessários para descobrir referências
    entre composições são retornados.
    """

    composition_code = serializers.CharField(
        source="composition.generic_item.code",
        read_only=True,
    )

    generic_item = serializers.CharField(
        source="generic_item.code",
        read_only=True,
    )

    class Meta:
        model = AuxiliaryActivityItem
        fields = [
            "composition_code",
            "generic_item",
            "input_quantity",
        ]


class EquipmentCalculationSerializer(
    serializers.ModelSerializer
):
    """
    Serializer mínimo utilizado pelo motor de cálculo.
    """

    composition_code = serializers.CharField(
        source="composition.generic_item.code",
        read_only=True,
    )

    generic_item = serializers.CharField(
        source="generic_item.code",
        read_only=True,
    )

    unit = serializers.CharField(
        source="unit.unit",
        read_only=True,
    )

    class Meta:
        model = EquipmentItem
        fields = [
            "composition_code",
            "input_group",
            "generic_item",
            "unit",
            "input_quantity",
            "input_use",
        ]


class WorkmanCalculationSerializer(
    serializers.ModelSerializer
):
    """
    Serializer mínimo utilizado pelo motor de cálculo.
    """

    composition_code = serializers.CharField(
        source="composition.generic_item.code",
        read_only=True,
    )

    generic_item = serializers.CharField(
        source="generic_item.code",
        read_only=True,
    )

    unit = serializers.CharField(
        source="unit.unit",
        read_only=True,
    )

    class Meta:
        model = WorkmanItem
        fields = [
            "composition_code",
            "input_group",
            "generic_item",
            "unit",
            "input_quantity",
        ]


class MaterialCalculationSerializer(
    serializers.ModelSerializer
):
    """
    Serializer mínimo utilizado pelo motor de cálculo.
    """

    composition_code = serializers.CharField(
        source="composition.generic_item.code",
        read_only=True,
    )

    generic_item = serializers.CharField(
        source="generic_item.code",
        read_only=True,
    )

    unit = serializers.CharField(
        source="unit.unit",
        read_only=True,
    )

    class Meta:
        model = MaterialItem
        fields = [
            "composition_code",
            "input_group",
            "generic_item",
            "unit",
            "input_quantity",
        ]


class TransportCalculationSerializer(
    serializers.ModelSerializer
):
    """
    Serializer mínimo utilizado pelo motor de cálculo.
    """

    composition_code = serializers.CharField(
        source="composition.generic_item.code",
        read_only=True,
    )

    generic_item = serializers.CharField(
        source="generic_item.code",
        read_only=True,
    )

    proprietary_item = serializers.CharField(
        source="proprietary_item.code",
        read_only=True,
    )

    unit = serializers.CharField(
        source="unit.unit",
        read_only=True,
    )

    class Meta:
        model = TransportItem
        fields = [
            "composition_code",
            "input_group",
            "generic_item",
            "unit",
            "input_quantity",
            "proprietary_item",
        ]