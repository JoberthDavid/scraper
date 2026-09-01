from collections import Counter
from decimal import Decimal

from django.test import TestCase

from core.models import (
    SourceFile,
    Composition,
    GenericItem,
    GenericDescription,
    Unit,
)

from core.usefuls.choices import (
    SICRO,
    GOIAS,
    ONERADO,
    ANALITICO,
    COMPOSICAO,
)


class AnalyticalCompositionDatabaseIntegrityTests(TestCase):

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base="2023-01-01",
            source_file="an.xlsx",
            type_system=ONERADO,
            type_file=ANALITICO,
            status=True,
        )

        self.unit = Unit.objects.create(
            unit="m3",
        )

    def create_composition(self, code, description):
        item = GenericItem.objects.create(
            code=code,
        )

        generic_description = GenericDescription.objects.create(
            description=description,
            group=COMPOSICAO,
        )

        item.source_files.add(
            self.source_file,
        )

        generic_description.source_files.add(
            self.source_file,
        )

        generic_description.generic_items.add(
            item,
        )

        composition = Composition.objects.create(
            generic_item=item,
            generic_description=generic_description,
            unit=self.unit,
            fic=Decimal("0.00000"),
            production=Decimal("1.00000"),
            composition_group=code[:2],
        )

        composition.source_files.add(
            self.source_file,
        )

        return composition

    def database_codes(self):
        return Counter(
            Composition.objects
            .filter(source_files=self.source_file)
            .values_list(
                "generic_item__code",
                flat=True,
            )
        )

    def test_same_codes_are_consistent(self):
        self.create_composition(
            "1100001",
            "Composição 1",
        )

        self.create_composition(
            "1100002",
            "Composição 2",
        )

        xlsx_codes = Counter([
            "1100001",
            "1100002",
        ])

        database_codes = self.database_codes()

        self.assertEqual(
            xlsx_codes,
            database_codes,
        )

    def test_missing_database_code_is_detected(self):
        self.create_composition(
            "1100001",
            "Composição 1",
        )

        xlsx_codes = Counter([
            "1100001",
            "1100002",
        ])

        database_codes = self.database_codes()

        self.assertEqual(
            xlsx_codes - database_codes,
            Counter({"1100002": 1}),
        )

    def test_extra_database_code_is_detected(self):
        self.create_composition(
            "1100001",
            "Composição 1",
        )

        self.create_composition(
            "1100002",
            "Composição 2",
        )

        xlsx_codes = Counter([
            "1100001",
        ])

        database_codes = self.database_codes()

        self.assertEqual(
            database_codes - xlsx_codes,
            Counter({"1100002": 1}),
        )

    def test_duplicate_occurrence_is_detected(self):
        self.create_composition(
            "1100001",
            "Composição 1",
        )

        self.create_composition(
            "1100002",
            "Composição 2",
        )

        xlsx_codes = Counter([
            "1100001",
            "1100001",
            "1100002",
        ])

        database_codes = self.database_codes()

        self.assertEqual(
            xlsx_codes - database_codes,
            Counter({"1100001": 1}),
        )