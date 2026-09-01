from decimal import Decimal

from django.test import TestCase

from core.models import (
    SourceFile,
    Unit,
    GenericItem,
    GenericDescription,
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
    CUSTO,
    PRECO,
    PRODUTIVO,
    IMPRODUTIVO,
)


class StandardMonetaryValueIntegrityTests(TestCase):
    """
    Tests the monetary-value structure used by synthetic,
    material and workman source files.
    """

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base="2023-01-01",
            source_file="teste.xlsx",
            type_system=ONERADO,
            type_file=SINTETICO,
            status=True,
        )

        self.unit = Unit.objects.create(
            unit="un",
        )

        self.item = GenericItem.objects.create(
            code="1100001",
        )

        self.description = GenericDescription.objects.create(
            description="Composição de teste",
            group=COMPOSICAO,
        )

        self.item.source_files.add(
            self.source_file,
        )

        self.description.source_files.add(
            self.source_file,
        )

        self.description.generic_items.add(
            self.item,
        )

    def create_monetary_value(
        self,
        *,
        value=Decimal("123.4567"),
        classification=PRECO,
        group=COMPOSICAO,
    ):
        return MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file,
            unit=self.unit,
            monetary_value=value,
            classification=classification,
            group=group,
            type_system=self.source_file.type_system,
        )

    def test_standard_item_has_one_monetary_value(self):
        self.create_monetary_value()

        values = MonetaryValue.objects.filter(
            generic_item=self.item,
            source_file=self.source_file,
        )

        self.assertEqual(
            values.count(),
            1,
        )

    def test_standard_item_monetary_value_matches_expected_value(self):
        self.create_monetary_value(
            value=Decimal("123.4567"),
        )

        monetary_value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
        )

        self.assertEqual(
            monetary_value.monetary_value,
            Decimal("123.4567"),
        )

    def test_standard_item_uses_correct_classification(self):
        self.create_monetary_value(
            classification=PRECO,
        )

        monetary_value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
        )

        self.assertEqual(
            monetary_value.classification,
            PRECO,
        )

    def test_standard_item_uses_correct_group(self):
        self.create_monetary_value(
            group=COMPOSICAO,
        )

        monetary_value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
        )

        self.assertEqual(
            monetary_value.group,
            COMPOSICAO,
        )

    def test_standard_item_is_related_to_source_file(self):
        self.create_monetary_value()

        monetary_value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
        )

        self.assertEqual(
            monetary_value.source_file,
            self.source_file,
        )

    def test_standard_item_is_related_to_correct_unit(self):
        self.create_monetary_value()

        monetary_value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
        )

        self.assertEqual(
            monetary_value.unit,
            self.unit,
        )


class EquipmentMonetaryValueIntegrityTests(TestCase):
    """
    Equipment must have exactly two monetary values:

        PRODUTIVO
        IMPRODUTIVO
    """

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base="2023-01-01",
            source_file="equipamento.xlsx",
            type_system=ONERADO,
            type_file=ANALITICO,
            status=True,
        )

        self.unit = Unit.objects.create(
            unit="h",
        )

        self.item = GenericItem.objects.create(
            code="E1001",
        )

    def create_equipment_value(
        self,
        classification,
        value,
    ):
        return MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file,
            unit=self.unit,
            monetary_value=value,
            classification=classification,
            group=EQUIPAMENTO,
            type_system=self.source_file.type_system,
        )

    def test_equipment_has_exactly_two_monetary_values(self):
        self.create_equipment_value(
            PRODUTIVO,
            Decimal("42.19300"),
        )

        self.create_equipment_value(
            IMPRODUTIVO,
            Decimal("28.02380"),
        )

        values = MonetaryValue.objects.filter(
            generic_item=self.item,
            source_file=self.source_file,
        )

        self.assertEqual(
            values.count(),
            2,
        )

    def test_equipment_has_one_productive_value(self):
        self.create_equipment_value(
            PRODUTIVO,
            Decimal("42.19300"),
        )

        self.create_equipment_value(
            IMPRODUTIVO,
            Decimal("28.02380"),
        )

        self.assertEqual(
            MonetaryValue.objects.filter(
                generic_item=self.item,
                source_file=self.source_file,
                classification=PRODUTIVO,
            ).count(),
            1,
        )

    def test_equipment_has_one_unproductive_value(self):
        self.create_equipment_value(
            PRODUTIVO,
            Decimal("42.19300"),
        )

        self.create_equipment_value(
            IMPRODUTIVO,
            Decimal("28.02380"),
        )

        self.assertEqual(
            MonetaryValue.objects.filter(
                generic_item=self.item,
                source_file=self.source_file,
                classification=IMPRODUTIVO,
            ).count(),
            1,
        )

    def test_equipment_productive_value_matches_expected_value(self):
        self.create_equipment_value(
            PRODUTIVO,
            Decimal("42.19300"),
        )

        self.create_equipment_value(
            IMPRODUTIVO,
            Decimal("28.02380"),
        )

        value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
            classification=PRODUTIVO,
        )

        self.assertEqual(
            value.monetary_value,
            Decimal("42.1930"),
        )

    def test_equipment_unproductive_value_matches_expected_value(self):
        self.create_equipment_value(
            PRODUTIVO,
            Decimal("42.19300"),
        )

        self.create_equipment_value(
            IMPRODUTIVO,
            Decimal("28.02380"),
        )

        value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
            classification=IMPRODUTIVO,
        )

        self.assertEqual(
            value.monetary_value,
            Decimal("28.0238"),
        )


class HistoricalMonetaryValueIntegrityTests(TestCase):
    """
    The same GenericItem may have different monetary values in
    different source files.
    """

    def setUp(self):
        self.source_file_2023 = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base="2023-01-01",
            source_file="2023.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        self.source_file_2024 = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base="2024-01-01",
            source_file="2024.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        self.unit = Unit.objects.create(
            unit="kg",
        )

        self.item = GenericItem.objects.create(
            code="M1001",
        )

    def test_same_item_preserves_different_historical_values(self):
        MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file_2023,
            unit=self.unit,
            monetary_value=Decimal("1.2345"),
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

        MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file_2024,
            unit=self.unit,
            monetary_value=Decimal("2.3456"),
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

        value_2023 = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file_2023,
            classification=CUSTO,
        )

        value_2024 = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file_2024,
            classification=CUSTO,
        )

        self.assertEqual(
            value_2023.monetary_value,
            Decimal("1.2345"),
        )

        self.assertEqual(
            value_2024.monetary_value,
            Decimal("2.3456"),
        )

        self.assertNotEqual(
            value_2023.monetary_value,
            value_2024.monetary_value,
        )
