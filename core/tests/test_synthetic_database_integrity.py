from decimal import Decimal

import pandas as pd

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
    SINTETICO,
    EQUIPAMENTO,
    MATERIAL,
    COMPOSICAO,
    CUSTO,
    PRECO,
    PRODUTIVO,
    IMPRODUTIVO,
)

from core.usefuls.synthetic_integrity import (
    audit_standard_synthetic_integrity,
    audit_equipment_integrity,
)


class StandardSyntheticDatabaseIntegrityTests(TestCase):

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base="2023-01-01",
            source_file="si.xlsx",
            type_system=ONERADO,
            type_file=SINTETICO,
            status=True,
        )

        self.unit = Unit.objects.create(
            unit="kg",
        )

        self.item = GenericItem.objects.create(
            code="M1001",
        )

        self.description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
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

        MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file,
            unit=self.unit,
            monetary_value=Decimal("12.3456"),
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

    def valid_dataframe(self):
        return pd.DataFrame(
            [
                [
                    "M1001",
                    "Cimento",
                    "kg",
                    12.3456,
                ],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

    def test_standard_audit_passes_for_valid_data(self):
        result = audit_standard_synthetic_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertTrue(
            result["passed"]
        )

    def test_missing_generic_item_is_detected(self):
        self.item.source_files.remove(
            self.source_file,
        )

        result = audit_standard_synthetic_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertIn(
            "M1001",
            result["missing_items"],
        )

        self.assertFalse(
            result["passed"]
        )

    def test_missing_description_relation_is_detected(self):
        self.description.generic_items.remove(
            self.item,
        )

        result = audit_standard_synthetic_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertIn(
            (
                "M1001",
                "Cimento",
            ),
            result["wrong_descriptions"],
        )

        self.assertFalse(
            result["passed"]
        )

    def test_missing_monetary_value_is_detected(self):
        MonetaryValue.objects.all().delete()

        result = audit_standard_synthetic_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertIn(
            "M1001",
            result["missing_values"],
        )

        self.assertFalse(
            result["passed"]
        )

    def test_wrong_monetary_value_is_detected(self):
        monetary_value = MonetaryValue.objects.get(
            generic_item=self.item,
            source_file=self.source_file,
        )

        monetary_value.monetary_value = Decimal(
            "99.9999"
        )

        monetary_value.save()

        result = audit_standard_synthetic_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertEqual(
            len(result["wrong_values"]),
            1,
        )

        self.assertFalse(
            result["passed"]
        )

    def test_duplicate_monetary_values_are_detected(self):
        MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file,
            unit=self.unit,
            monetary_value=Decimal("12.3456"),
            classification=PRECO,
            group=COMPOSICAO,
            type_system=ONERADO,
        )

        result = audit_standard_synthetic_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertIn(
            ("M1001", 2),
            result["duplicate_values"],
        )

        self.assertFalse(
            result["passed"]
        )

    def test_inconsistent_duplicate_rows_are_detected(self):
        dataframe = pd.DataFrame(
            [
                [
                    "M1001",
                    "Cimento",
                    "kg",
                    12.3456,
                ],
                [
                    "M1001",
                    "Cimento",
                    "kg",
                    99.9999,
                ],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

        result = audit_standard_synthetic_integrity(
            self.source_file,
            dataframe,
        )

        self.assertIn(
            "M1001",
            result["inconsistent_duplicates"],
        )

        self.assertFalse(
            result["passed"]
        )


class EquipmentDatabaseIntegrityTests(TestCase):

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base="2023-01-01",
            source_file="eq.xlsx",
            type_system=ONERADO,
            type_file=EQUIPAMENTO,
            status=True,
        )

        self.unit = Unit.objects.create(
            unit="h",
        )

        self.item = GenericItem.objects.create(
            code="E1001",
        )

        self.description = GenericDescription.objects.create(
            description="Escavadeira",
            group=EQUIPAMENTO,
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

    def valid_dataframe(self):
        return pd.DataFrame(
            [
                [
                    "E1001",
                    "Escavadeira",
                    "h",
                    42.1930,
                    28.0238,
                ],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "productive_cost",
                "unproductive_cost",
            ],
        )

    def create_productive_value(
        self,
        value=Decimal("42.1930"),
    ):
        return MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file,
            unit=self.unit,
            monetary_value=value,
            classification=PRODUTIVO,
            group=EQUIPAMENTO,
            type_system=ONERADO,
        )

    def create_unproductive_value(
        self,
        value=Decimal("28.0238"),
    ):
        return MonetaryValue.objects.create(
            generic_item=self.item,
            source_file=self.source_file,
            unit=self.unit,
            monetary_value=value,
            classification=IMPRODUTIVO,
            group=EQUIPAMENTO,
            type_system=ONERADO,
        )

    def create_valid_monetary_structure(self):
        self.create_productive_value()
        self.create_unproductive_value()

    def test_equipment_audit_passes_for_valid_data(self):
        self.create_valid_monetary_structure()

        result = audit_equipment_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertTrue(
            result["passed"]
        )

    def test_missing_productive_value_is_detected(self):
        self.create_unproductive_value()

        result = audit_equipment_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertFalse(
            result["passed"]
        )

        self.assertTrue(
            result["wrong_monetary_structure"]
        )

    def test_missing_unproductive_value_is_detected(self):
        self.create_productive_value()

        result = audit_equipment_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertFalse(
            result["passed"]
        )

        self.assertTrue(
            result["wrong_monetary_structure"]
        )

    def test_wrong_productive_value_is_detected(self):
        self.create_productive_value(
            value=Decimal("99.9999")
        )

        self.create_unproductive_value()

        result = audit_equipment_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertFalse(
            result["passed"]
        )

        self.assertEqual(
            result["wrong_values"][0][1],
            PRODUTIVO,
        )

    def test_wrong_unproductive_value_is_detected(self):
        self.create_productive_value()

        self.create_unproductive_value(
            value=Decimal("99.9999")
        )

        result = audit_equipment_integrity(
            self.source_file,
            self.valid_dataframe(),
        )

        self.assertFalse(
            result["passed"]
        )

        self.assertEqual(
            result["wrong_values"][0][1],
            IMPRODUTIVO,
        )
