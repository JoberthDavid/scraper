from datetime import date
from decimal import Decimal

from django.test import TestCase

from core.models import (
    SourceFile,
    GenericItem,
    GenericDescription,
    MonetaryValue,
    Composition,
    Unit,
)

from core.usefuls.choices import (
    SICRO,
    GOIAS,
    DISTRITO_FEDERAL,
    ONERADO,
    DESONERADO,
    ANALITICO,
    SINTETICO,
    MATERIAL,
    COMPOSICAO,
    CUSTO,
)

from core.api.filters import (
    SourceFileFilter,
    GenericItemFilter,
    GenericDescriptionFilter,
    MonetaryValueFilter,
    CompositionFilter,
)


class SourceFileFilterTests(TestCase):

    def setUp(self):
        self.source_2023 = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="si_2023.xlsx",
            type_system=ONERADO,
            type_file=SINTETICO,
            status=True,
        )

        self.source_2024 = SourceFile.objects.create(
            methodology=SICRO,
            uf=DISTRITO_FEDERAL,
            data_base=date(2024, 7, 1),
            source_file="si_2024.xlsx",
            type_system=DESONERADO,
            type_file=ANALITICO,
            status=True,
        )

    def test_filter_by_minimum_year(self):
        queryset = SourceFile.objects.all()

        filtered = SourceFileFilter(
            data={
                "data_base__year__gte": 2024,
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            list(filtered),
            [self.source_2024],
        )

    def test_filter_by_methodology_prefix(self):
        queryset = SourceFile.objects.all()

        filtered = SourceFileFilter(
            data={
                "methodology__startswith": SICRO,
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            filtered.count(),
            2,
        )

    def test_filter_by_uf_prefix(self):
        queryset = SourceFile.objects.all()

        filtered = SourceFileFilter(
            data={
                "uf__startswith": DISTRITO_FEDERAL,
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            list(filtered),
            [self.source_2024],
        )

    def test_filter_by_type_system_prefix(self):
        queryset = SourceFile.objects.all()

        filtered = SourceFileFilter(
            data={
                "type_system__startswith": ONERADO,
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            list(filtered),
            [self.source_2023],
        )

    def test_filter_by_type_file_prefix(self):
        queryset = SourceFile.objects.all()

        filtered = SourceFileFilter(
            data={
                "type_file__startswith": ANALITICO,
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            list(filtered),
            [self.source_2024],
        )


class GenericItemFilterTests(TestCase):

    def setUp(self):
        self.source_2023 = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="ma_2023.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        self.source_2024 = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2024, 7, 1),
            source_file="ma_2024.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        self.item_1 = GenericItem.objects.create(
            code="M1001",
        )

        self.item_2 = GenericItem.objects.create(
            code="M2001",
        )

        self.description_1 = GenericDescription.objects.create(
            description="Cimento Portland",
            group=MATERIAL,
        )

        self.description_2 = GenericDescription.objects.create(
            description="Areia média",
            group=MATERIAL,
        )

        self.item_1.source_files.add(
            self.source_2023,
        )

        self.item_2.source_files.add(
            self.source_2024,
        )

        self.description_1.generic_items.add(
            self.item_1,
        )

        self.description_2.generic_items.add(
            self.item_2,
        )

    def test_filter_by_source_file_date(self):
        queryset = GenericItem.objects.all()

        filtered = GenericItemFilter(
            data={
                "source_files": "2023-07-01",
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            list(filtered),
            [self.item_1],
        )

    def test_filter_by_code_prefix(self):
        queryset = GenericItem.objects.all()

        filtered = GenericItemFilter(
            data={
                "code": "M1",
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            list(filtered),
            [self.item_1],
        )

    def test_filter_by_description_prefix(self):
        queryset = GenericItem.objects.all()

        filtered = GenericItemFilter(
            data={
                "descriptions": "Cimento",
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            list(filtered),
            [self.item_1],
        )

    def test_filter_by_description_group_prefix(self):
        queryset = GenericItem.objects.all()

        filtered = GenericItemFilter(
            data={
                "descriptions__group": MATERIAL,
            },
            queryset=queryset,
        ).qs

        self.assertEqual(
            filtered.count(),
            2,
        )


class GenericDescriptionFilterTests(TestCase):

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="ma_2023.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        self.material_item = GenericItem.objects.create(
            code="M1001",
        )

        self.composition_item = GenericItem.objects.create(
            code="1100001",
        )

        self.material_description = GenericDescription.objects.create(
            description="Cimento Portland",
            group=MATERIAL,
        )

        self.composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        self.material_description.source_files.add(
            self.source_file,
        )

        self.composition_description.source_files.add(
            self.source_file,
        )

        self.material_description.generic_items.add(
            self.material_item,
        )

        self.composition_description.generic_items.add(
            self.composition_item,
        )

    def test_filter_by_source_file_date(self):
        filtered = GenericDescriptionFilter(
            data={
                "source_files": "2023-07-01",
            },
            queryset=GenericDescription.objects.all(),
        ).qs

        self.assertEqual(
            filtered.count(),
            2,
        )

    def test_filter_by_group_prefix(self):
        filtered = GenericDescriptionFilter(
            data={
                "group": MATERIAL,
            },
            queryset=GenericDescription.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.material_description],
        )

    def test_filter_by_generic_item_code_prefix(self):
        filtered = GenericDescriptionFilter(
            data={
                "generic_item": "M1",
            },
            queryset=GenericDescription.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.material_description],
        )

    def test_filter_by_description_prefix(self):
        filtered = GenericDescriptionFilter(
            data={
                "description": "Cimento",
            },
            queryset=GenericDescription.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.material_description],
        )


class MonetaryValueFilterTests(TestCase):

    def setUp(self):
        self.source_2023 = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="ma_2023.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        self.source_2024 = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2024, 7, 1),
            source_file="ma_2024.xlsx",
            type_system=ONERADO,
            type_file=MATERIAL,
            status=True,
        )

        self.item_1 = GenericItem.objects.create(
            code="M1001",
        )

        self.item_2 = GenericItem.objects.create(
            code="M2001",
        )

        self.unit_kg = Unit.objects.create(
            unit="kg",
        )

        self.unit_m3 = Unit.objects.create(
            unit="m3",
        )

        self.value_2023 = MonetaryValue.objects.create(
            generic_item=self.item_1,
            source_file=self.source_2023,
            unit=self.unit_kg,
            monetary_value=Decimal("1.2500"),
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

        self.value_2024 = MonetaryValue.objects.create(
            generic_item=self.item_2,
            source_file=self.source_2024,
            unit=self.unit_m3,
            monetary_value=Decimal("80.0000"),
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

    def test_source_file_filter_uses_database_date(self):
        """
        A classe declara source_file duas vezes.

        A segunda declaração, DateFilter(data_base__exact),
        sobrescreve a primeira declaração CharFilter(startswith).

        Portanto, o comportamento efetivo é filtrar pela data-base.
        """

        filtered = MonetaryValueFilter(
            data={
                "source_file": "2023-07-01",
            },
            queryset=MonetaryValue.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.value_2023],
        )

    def test_filter_by_classification_prefix(self):
        filtered = MonetaryValueFilter(
            data={
                "classification": CUSTO,
            },
            queryset=MonetaryValue.objects.all(),
        ).qs

        self.assertEqual(
            filtered.count(),
            2,
        )

    def test_filter_by_group_prefix(self):
        filtered = MonetaryValueFilter(
            data={
                "group": MATERIAL,
            },
            queryset=MonetaryValue.objects.all(),
        ).qs

        self.assertEqual(
            filtered.count(),
            2,
        )

    def test_filter_by_generic_item_code_prefix(self):
        filtered = MonetaryValueFilter(
            data={
                "generic_item": "M1",
            },
            queryset=MonetaryValue.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.value_2023],
        )

    def test_filter_by_unit_prefix(self):
        filtered = MonetaryValueFilter(
            data={
                "unit": "kg",
            },
            queryset=MonetaryValue.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.value_2023],
        )


class CompositionFilterTests(TestCase):

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            uf=GOIAS,
            data_base=date(2023, 7, 1),
            source_file="si_2023.xlsx",
            type_system=ONERADO,
            type_file=ANALITICO,
            status=True,
        )

        self.unit = Unit.objects.create(
            unit="m3",
        )

        self.item = GenericItem.objects.create(
            code="1100001",
        )

        self.description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        self.composition = Composition.objects.create(
            generic_item=self.item,
            generic_description=self.description,
            unit=self.unit,
            fic=Decimal("0.10000"),
            production=Decimal("24.63000"),
            composition_group="11",
        )

        self.composition.source_files.add(
            self.source_file,
        )

    def test_filter_by_source_file_date(self):
        filtered = CompositionFilter(
            data={
                "source_files__data_base": "2023-07-01",
            },
            queryset=Composition.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.composition],
        )

    def test_filter_by_composition_group_prefix(self):
        filtered = CompositionFilter(
            data={
                "composition_group": "1",
            },
            queryset=Composition.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.composition],
        )

    def test_filter_by_generic_item_code_exact(self):
        filtered = CompositionFilter(
            data={
                "generic_item__code": "1100001",
            },
            queryset=Composition.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.composition],
        )

    def test_filter_by_generic_description_prefix(self):
        filtered = CompositionFilter(
            data={
                "generic_description__description": "Execução",
            },
            queryset=Composition.objects.all(),
        ).qs

        self.assertEqual(
            list(filtered),
            [self.composition],
        )