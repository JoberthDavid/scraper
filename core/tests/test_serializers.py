from decimal import Decimal
from datetime import date

from django.test import TestCase
from rest_framework.serializers import ModelSerializer

from core.models import (
    SourceFile,
    Composition,
    EquipmentItem,
    WorkmanItem,
    MaterialItem,
    AuxiliaryActivityItem,
    TransportItem,
    GenericItem,
    GenericDescription,
    Unit,
    MonetaryValue,
)

from core.usefuls.choices import (
    SICRO,
    GOIAS,
    ONERADO,
    ANALITICO,
    SINTETICO,
    EQUIPAMENTO,
    MAODEOBRA,
    MATERIAL,
    COMPOSICAO,
    AUXILIAR,
    TEMPO_FIXO,
)


from core.api.serializers import (
    SourceFileFullyDetailedSerializer,
    SourceFilePartiallyDetailedSerializer,
    GenericDescriptionSerializer,
    GenericItemSerializer,
    UnitSerializer,
    MonetaryValueSerializer,
    EquipmentItemSerializer,
    WorkmanItemSerializer,
    MaterialItemSerializer,
    AuxiliaryActivityItemSerializer,
    TransportItemSerializer,
    CompositionSerializer,
)


class SourceFileSerializerTests(TestCase):

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="teste.xlsx",
            type_system=ONERADO,
            type_file=ANALITICO,
            status=True,
        )

    def test_fully_detailed_serializer_returns_expected_fields(self):
        serializer = SourceFileFullyDetailedSerializer(
            self.source_file,
        )

        data = serializer.data

        self.assertEqual(
            data["id"],
            self.source_file.id,
        )

        self.assertEqual(
            data["methodology"],
            SICRO,
        )

        self.assertEqual(
            data["uf"],
            GOIAS,
        )

        self.assertEqual(
            data["data_base"],
            "2023-07-01",
        )

        self.assertIn(
            "teste.xlsx",
            data["source_file"],
        )

        self.assertEqual(
            data["type_system"],
            ONERADO,
        )

        self.assertEqual(
            data["type_file"],
            ANALITICO,
        )

        self.assertTrue(
            data["status"],
        )

        
    def test_partially_detailed_serializer_returns_expected_fields(self):
        serializer = SourceFilePartiallyDetailedSerializer(
            self.source_file,
        )

        self.assertEqual(
            serializer.data,
            {
                "id": self.source_file.id,
                "uf": GOIAS,
                "data_base": "2023-07-01",
            },
        )


class UnitSerializerTests(TestCase):

    def test_unit_serializer_returns_expected_fields(self):
        unit = Unit.objects.create(
            unit="kg",
            dimensional="massa",
        )

        serializer = UnitSerializer(unit)

        self.assertEqual(
            serializer.data["id"],
            unit.id,
        )

        self.assertEqual(
            serializer.data["unit"],
            "kg",
        )

        self.assertEqual(
            serializer.data["dimensional"],
            "massa",
        )


class GenericItemSerializerTests(TestCase):

    def test_generic_item_serializer_returns_code_and_source_file_dates(self):
        source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="teste.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        item = GenericItem.objects.create(
            code="M1001",
        )

        description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        item.source_files.add(
            source_file,
        )

        description.source_files.add(
            source_file,
        )

        description.generic_items.add(
            item,
        )

        serializer = GenericItemSerializer(item)

        data = serializer.data

        self.assertEqual(
            data["code"],
            "M1001",
        )

        self.assertEqual(
            data["source_files"],
            [date(2023, 7, 1)],
        )

        self.assertEqual(
            len(data["descriptions"]),
            1,
        )

        self.assertEqual(
            data["descriptions"][0]["description"],
            "Cimento",
        )

        self.assertEqual(
            data["descriptions"][0]["group"],
            MATERIAL,
        )


class GenericDescriptionSerializerTests(TestCase):

    def test_generic_description_serializer_returns_related_code_and_source_file_dates(self):
        source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="teste.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        item = GenericItem.objects.create(
            code="M1001",
        )

        description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        item.source_files.add(
            source_file,
        )

        description.source_files.add(
            source_file,
        )

        description.generic_items.add(
            item,
        )

        serializer = GenericDescriptionSerializer(
            description,
        )

        data = serializer.data


        self.assertEqual(
            data["source_files"],
            [date(2023, 7, 1)],
        )

        self.assertEqual(
            data["group"],
            MATERIAL,
        )

        self.assertEqual(
            data["description"],
            "Cimento",
        )

class MonetaryValueSerializerTests(TestCase):

    def test_monetary_value_serializer_returns_nested_source_file_code_and_unit(self):
        source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="teste.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        item = GenericItem.objects.create(
            code="M1001",
        )

        unit = Unit.objects.create(
            unit="kg",
        )

        monetary_value = MonetaryValue.objects.create(
            generic_item=item,
            source_file=source_file,
            unit=unit,
            monetary_value=Decimal("1.2500"),
            classification="CU",
            group=MATERIAL,
            type_system=ONERADO,
        )

        serializer = MonetaryValueSerializer(
            monetary_value,
        )

        data = serializer.data

        self.assertEqual(
            data["generic_item"],
            "M1001",
        )

        self.assertEqual(
            data["unit"],
            "kg",
        )

        self.assertEqual(
            data["source_file"]["id"],
            source_file.id,
        )

        self.assertEqual(
            data["source_file"]["uf"],
            GOIAS,
        )

        self.assertEqual(
            data["source_file"]["data_base"],
            "2023-07-01",
        )

        self.assertEqual(
            data["monetary_value"],
            "1.2500",
        )

        self.assertEqual(
            data["group"],
            MATERIAL,
        )


class InputItemSerializerTests(TestCase):

    def setUp(self):
        self.composition_item = GenericItem.objects.create(
            code="1100001",
        )

        self.composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        self.unit = Unit.objects.create(
            unit="m3",
        )

        self.composition = Composition.objects.create(
            generic_item=self.composition_item,
            generic_description=self.composition_description,
            unit=self.unit,
            fic=Decimal("0.10000"),
            production=Decimal("24.63000"),
            composition_group="11",
        )

        self.item = GenericItem.objects.create(
            code="E1001",
        )

        self.description = GenericDescription.objects.create(
            description="Escavadeira",
            group=EQUIPAMENTO,
        )

        self.item.source_files.clear()
        self.description.source_files.clear()

    def test_equipment_serializer_returns_related_values(self):
        unit = Unit.objects.create(
            unit="h",
        )

        equipment = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.item,
            generic_description=self.description,
            unit=unit,
            input_quantity=Decimal("1.50000"),
            input_use=Decimal("2.00000"),
            input_group=EQUIPAMENTO,
        )

        serializer = EquipmentItemSerializer(equipment)

        self.assertEqual(
            serializer.data["generic_item"],
            "E1001",
        )

        self.assertEqual(
            serializer.data["generic_description"],
            str(self.description),
        )

        self.assertEqual(
            serializer.data["unit"],
            "h",
        )

        self.assertEqual(
            serializer.data["input_quantity"],
            "1.50000",
        )

        self.assertEqual(
            serializer.data["input_use"],
            "2.00000",
        )

        self.assertEqual(
            serializer.data["input_group"],
            EQUIPAMENTO,
        )


class CompositionSerializerTests(TestCase):

    def setUp(self):
        self.composition_item = GenericItem.objects.create(
            code="1100001",
        )

        self.composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        self.composition_unit = Unit.objects.create(
            unit="m3",
        )

        self.composition = Composition.objects.create(
            generic_item=self.composition_item,
            generic_description=self.composition_description,
            unit=self.composition_unit,
            fic=Decimal("0.10000"),
            production=Decimal("24.63000"),
            composition_group="11",
        )

    def test_composition_serializer_returns_basic_fields(self):
        serializer = CompositionSerializer(
            self.composition,
        )

        data = serializer.data

        self.assertEqual(
            data["generic_item"],
            "1100001",
        )

        self.assertEqual(
            data["generic_description"],
            str(self.composition_description),
        )

        self.assertEqual(
            data["unit"],
            "m3",
        )

        self.assertEqual(
            data["fic"],
            "0.10000",
        )

        self.assertEqual(
            data["production"],
            "24.63000",
        )

        self.assertEqual(
            data["composition_group"],
            "11",
        )

    def test_composition_serializer_includes_all_input_collections(self):
        equipment_unit = Unit.objects.create(
            unit="h",
        )

        equipment_item = GenericItem.objects.create(
            code="E1001",
        )

        equipment_description = GenericDescription.objects.create(
            description="Escavadeira",
            group=EQUIPAMENTO,
        )

        EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=equipment_item,
            generic_description=equipment_description,
            unit=equipment_unit,
            input_quantity=Decimal("1.50000"),
            input_use=Decimal("2.00000"),
            input_group=EQUIPAMENTO,
        )

        workman_item = GenericItem.objects.create(
            code="P9821",
        )

        workman_description = GenericDescription.objects.create(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        WorkmanItem.objects.create(
            composition=self.composition,
            generic_item=workman_item,
            generic_description=workman_description,
            unit=equipment_unit,
            input_quantity=Decimal("1.00000"),
            input_group=MAODEOBRA,
        )

        material_item = GenericItem.objects.create(
            code="M1001",
        )

        material_description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        material_unit = Unit.objects.create(
            unit="kg",
        )

        MaterialItem.objects.create(
            composition=self.composition,
            generic_item=material_item,
            generic_description=material_description,
            unit=material_unit,
            input_quantity=Decimal("2.50000"),
            input_group=MATERIAL,
        )

        activity_item = GenericItem.objects.create(
            code="1107928",
        )

        activity_description = GenericDescription.objects.create(
            description="Concreto fck = 20 MPa",
            group=MATERIAL,
        )

        AuxiliaryActivityItem.objects.create(
            composition=self.composition,
            generic_item=activity_item,
            generic_description=activity_description,
            unit=self.composition_unit,
            input_quantity=Decimal("0.13900"),
            input_group=AUXILIAR,
        )

        transport_item = GenericItem.objects.create(
            code="5914569",
        )

        transport_description = GenericDescription.objects.create(
            description="Transporte",
            group=COMPOSICAO,
        )

        proprietary_item = activity_item

        transport_unit = Unit.objects.create(
            unit="tkm",
        )

        TransportItem.objects.create(
            composition=self.composition,
            generic_item=transport_item,
            generic_description=transport_description,
            unit=transport_unit,
            input_quantity=Decimal("0.33360"),
            input_group=TEMPO_FIXO,
            proprietary_item=proprietary_item,
        )

        serializer = CompositionSerializer(
            self.composition,
        )

        data = serializer.data

        self.assertEqual(
            len(data["equipments"]),
            1,
        )

        self.assertEqual(
            len(data["workmen"]),
            1,
        )

        self.assertEqual(
            len(data["materials"]),
            1,
        )

        self.assertEqual(
            len(data["activities"]),
            1,
        )

        self.assertEqual(
            len(data["transports"]),
            1,
        )

        self.assertEqual(
            data["equipments"][0]["generic_item"],
            "E1001",
        )

        self.assertEqual(
            data["workmen"][0]["generic_item"],
            "P9821",
        )

        self.assertEqual(
            data["materials"][0]["generic_item"],
            "M1001",
        )

        self.assertEqual(
            data["activities"][0]["generic_item"],
            "1107928",
        )

        self.assertEqual(
            data["transports"][0]["generic_item"],
            "5914569",
        )