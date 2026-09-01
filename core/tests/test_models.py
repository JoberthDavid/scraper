"""
Testes dos Models da aplicação core.

Objetivo:
    Validar o comportamento atual dos Models sem modificar sua modelagem.

    Estes testes são deliberadamente orientados ao comportamento existente
    da aplicação, incluindo as particularidades da estrutura de dados
    provenientes das bases SICRO/SINAPI.

Executar com:

    python manage.py test core.tests_models
"""

from decimal import Decimal
from datetime import date

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase

from core.models import (
    SourceFile,
    Unit,
    GenericItem,
    GenericDescription,
    MonetaryValue,
    Composition,
    EquipmentItem,
    WorkmanItem,
    MaterialItem,
    AuxiliaryActivityItem,
    TransportItem,
)

from core.usefuls.choices import (
    SICRO,
    SINAPI,
    ANALITICO,
    SINTETICO,
    COMPOSICAO,
    EQUIPAMENTO,
    MAODEOBRA,
    MATERIAL,
    AUXILIAR,
    ONERADO,
    DESONERADO,
    NAO_APLICAVEL,
    CUSTO,
    PRECO,
    GOIAS,
    DISTRITO_FEDERAL,
)


# ============================================================================
# DADOS AUXILIARES
# ============================================================================

DATA_BASE_2023_07 = date(2023, 7, 1)
DATA_BASE_2024_01 = date(2024, 1, 1)

FILE_NAME_1 = "base_07_2023.xlsx"
FILE_NAME_2 = "base_01_2024.xlsx"


def create_source_file(
    *,
    methodology=SICRO,
    data_base=DATA_BASE_2023_07,
    file_name=FILE_NAME_1,
    uf=GOIAS,
    type_system=ONERADO,
    type_file=ANALITICO,
    status=False,
    number_of_lines_to_skip=0,
):
    """
    Cria uma SourceFile válida para os testes.

    Não precisamos gravar um XLSX real no storage para testar os Models.
    Um nome de arquivo válido é suficiente para os testes de persistência.
    """

    return SourceFile.objects.create(
        methodology=methodology,
        data_base=data_base,
        source_file=file_name,
        uf=uf,
        type_system=type_system,
        type_file=type_file,
        status=status,
        number_of_lines_to_skip=number_of_lines_to_skip,
    )


def create_unit(
    *,
    unit="h",
    dimensional=None,
):
    return Unit.objects.create(
        unit=unit,
        dimensional=dimensional,
    )


def create_generic_item(
    *,
    code="P9821",
):
    return GenericItem.objects.create(
        code=code,
    )


def create_generic_description(
    *,
    description="Pedreiro",
    group=MAODEOBRA,
):
    return GenericDescription.objects.create(
        description=description,
        group=group,
    )


def create_composition(
    *,
    code="00000001",
    description="Composição de teste",
    unit="m3",
    dimensional="volume",
    fic=Decimal("0.00000"),
    production=Decimal("10.00000"),
    composition_group="11",
    source_file=None,
):
    """
    Cria uma Composition e seus objetos básicos.

    O código da composição é mantido no GenericItem, conforme a modelagem
    atual do projeto.
    """

    if source_file is None:
        source_file = create_source_file()

    generic_item = create_generic_item(code=code)

    generic_description = create_generic_description(
        description=description,
        group=COMPOSICAO,
    )

    unit_obj = create_unit(
        unit=unit,
        dimensional=dimensional,
    )

    composition = Composition.objects.create(
        generic_item=generic_item,
        generic_description=generic_description,
        unit=unit_obj,
        fic=fic,
        production=production,
        composition_group=composition_group,
    )

    composition.source_files.add(source_file)

    return composition


# ============================================================================
# SOURCE FILE
# ============================================================================

class SourceFileModelTests(TestCase):
    """Testes do Model SourceFile."""

    def test_create_source_file(self):
        source_file = create_source_file()

        self.assertIsNotNone(source_file.pk)
        self.assertEqual(source_file.methodology, SICRO)
        self.assertEqual(source_file.data_base, DATA_BASE_2023_07)
        self.assertEqual(source_file.uf, GOIAS)
        self.assertEqual(source_file.type_system, ONERADO)
        self.assertEqual(source_file.type_file, ANALITICO)
        self.assertFalse(source_file.status)
        self.assertEqual(source_file.number_of_lines_to_skip, 0)

    def test_default_status(self):
        source_file = create_source_file()

        self.assertFalse(source_file.status)

    def test_default_number_of_lines_to_skip(self):
        source_file = create_source_file()

        self.assertEqual(source_file.number_of_lines_to_skip, 0)

    def test_format_data_base(self):
        source_file = create_source_file(
            data_base=date(2023, 7, 1)
        )

        self.assertEqual(
            source_file.format_data_base(),
            "07/2023",
        )

    def test_parser_data_base_to_string(self):
        source_file = create_source_file(
            data_base=date(2023, 7, 1)
        )

        self.assertEqual(
            source_file.parser_data_base_to_string(),
            "07/2023",
        )

    def test_str(self):
        source_file = create_source_file(
            methodology=SICRO,
            data_base=date(2023, 7, 1),
            uf=DISTRITO_FEDERAL,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        expected = " - ".join(
            [
                source_file.methodology,
                source_file.uf,
                source_file.parser_data_base_to_string(),
                source_file.type_system,
                source_file.type_file,
            ]
        )

        self.assertEqual(str(source_file), expected)

    def test_get_absolute_url(self):
        source_file = create_source_file()

        self.assertEqual(
            source_file.get_absolute_url(),
            f"/scraper/{source_file.pk}/",
        )

    def test_unique_source_file_constraint(self):
        """
        A combinação:

            methodology
            data_base
            type_system
            type_file

        deve ser única.

        Isso é uma regra deliberada do Model atual.
        """

        create_source_file(
            methodology=SICRO,
            data_base=DATA_BASE_2023_07,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        with self.assertRaises(IntegrityError):
            create_source_file(
                methodology=SICRO,
                data_base=DATA_BASE_2023_07,
                type_system=ONERADO,
                type_file=ANALITICO,
                uf=DISTRITO_FEDERAL,
            )

    def test_same_data_base_can_have_different_type_system(self):
        source_onerado = create_source_file(
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        source_desonerado = create_source_file(
            type_system=DESONERADO,
            type_file=ANALITICO,
        )

        self.assertNotEqual(
            source_onerado.pk,
            source_desonerado.pk,
        )

    def test_same_data_base_can_have_different_type_file(self):
        source_analitico = create_source_file(
            type_file=ANALITICO,
        )

        source_sintetico = create_source_file(
            type_file=SINTETICO,
        )

        self.assertNotEqual(
            source_analitico.pk,
            source_sintetico.pk,
        )

    def test_file_extension_validator_accepts_xlsx(self):
        source_file = SourceFile(
            methodology=SICRO,
            data_base=DATA_BASE_2023_07,
            source_file=SimpleUploadedFile(
                "arquivo.xlsx",
                b"conteudo",
                content_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            ),
            uf=GOIAS,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        # Não deve gerar ValidationError relacionado à extensão.
        source_file.full_clean()


# ============================================================================
# UNIT
# ============================================================================

class UnitModelTests(TestCase):
    """Testes do Model Unit."""

    def test_create_unit(self):
        unit = create_unit(
            unit="m2",
            dimensional="área",
        )

        self.assertIsNotNone(unit.pk)
        self.assertEqual(unit.unit, "m2")
        self.assertEqual(unit.dimensional, "área")

    def test_str(self):
        unit = create_unit(unit="m2")

        self.assertEqual(str(unit), "m2")

    def test_unit_is_unique(self):
        create_unit(unit="m2")

        with self.assertRaises(IntegrityError):
            create_unit(unit="m2")

    def test_dimensional_can_be_null(self):
        unit = create_unit(
            unit="h",
            dimensional=None,
        )

        self.assertIsNone(unit.dimensional)


# ============================================================================
# GENERIC ITEM
# ============================================================================

class GenericItemModelTests(TestCase):
    """Testes do Model GenericItem."""

    def test_create_generic_item(self):
        item = create_generic_item(
            code="P9821",
        )

        self.assertIsNotNone(item.pk)
        self.assertEqual(item.code, "P9821")

    def test_str(self):
        item = create_generic_item(
            code="P9821",
        )

        self.assertEqual(str(item), "P9821")

    def test_code_is_unique(self):
        create_generic_item(
            code="P9821",
        )

        with self.assertRaises(IntegrityError):
            create_generic_item(
                code="P9821",
            )

    def test_code_can_be_related_to_multiple_source_files(self):
        item = create_generic_item(
            code="P9821",
        )

        source_1 = create_source_file(
            data_base=DATA_BASE_2023_07,
            type_file=ANALITICO,
        )

        source_2 = create_source_file(
            data_base=DATA_BASE_2024_01,
            type_file=ANALITICO,
        )

        item.source_files.add(source_1, source_2)

        self.assertEqual(item.source_files.count(), 2)
        self.assertIn(source_1, item.source_files.all())
        self.assertIn(source_2, item.source_files.all())


# ============================================================================
# GENERIC DESCRIPTION
# ============================================================================

class GenericDescriptionModelTests(TestCase):
    """Testes do Model GenericDescription."""

    def test_create_generic_description(self):
        description = create_generic_description(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        self.assertIsNotNone(description.pk)
        self.assertEqual(description.description, "Pedreiro")
        self.assertEqual(description.group, MAODEOBRA)

    def test_str(self):
        description = create_generic_description(
            description="Pedreiro",
        )

        self.assertEqual(
            str(description),
            "Pedreiro",
        )

    def test_description_is_unique(self):
        """
        O campo description possui unique=True.

        Portanto uma mesma descrição textual representa um único
        GenericDescription, podendo ser relacionada a vários GenericItem.
        """

        create_generic_description(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        with self.assertRaises(IntegrityError):
            create_generic_description(
                description="Pedreiro",
                group=MAODEOBRA,
            )

    def test_same_description_can_be_shared_by_multiple_items(self):
        """
        Este teste é particularmente importante para a arquitetura
        atual do banco.

        A descrição NÃO deve ser duplicada para cada código.

        Exemplo:

            P9821 -> Pedreiro
            P9822 -> Pedreiro

        Os dois códigos podem apontar para o mesmo GenericDescription.
        """

        description = create_generic_description(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        item_1 = create_generic_item(code="P9821")
        item_2 = create_generic_item(code="P9822")

        description.generic_items.add(
            item_1,
            item_2,
        )

        self.assertEqual(
            description.generic_items.count(),
            2,
        )

        self.assertIn(
            item_1,
            description.generic_items.all(),
        )

        self.assertIn(
            item_2,
            description.generic_items.all(),
        )

    def test_description_can_be_related_to_multiple_source_files(self):
        description = create_generic_description(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        source_1 = create_source_file(
            data_base=DATA_BASE_2023_07,
        )

        source_2 = create_source_file(
            data_base=DATA_BASE_2024_01,
        )

        description.source_files.add(
            source_1,
            source_2,
        )

        self.assertEqual(
            description.source_files.count(),
            2,
        )


# ============================================================================
# MONETARY VALUE
# ============================================================================

class MonetaryValueModelTests(TestCase):
    """Testes do Model MonetaryValue."""

    def setUp(self):
        self.source_file = create_source_file()

        self.generic_item = create_generic_item(
            code="P9821",
        )

        self.unit = create_unit(
            unit="h",
            dimensional=None,
        )

    def test_create_monetary_value(self):
        value = MonetaryValue.objects.create(
            generic_item=self.generic_item,
            source_file=self.source_file,
            monetary_value=Decimal("35.1234"),
            unit=self.unit,
            classification=CUSTO,
            group=MAODEOBRA,
            type_system=ONERADO,
        )

        self.assertIsNotNone(value.pk)
        self.assertEqual(
            value.monetary_value,
            Decimal("35.1234"),
        )

    def test_default_monetary_value(self):
        value = MonetaryValue.objects.create(
            generic_item=self.generic_item,
            source_file=self.source_file,
            unit=self.unit,
            classification=CUSTO,
            group=MAODEOBRA,
            type_system=ONERADO,
        )

        self.assertEqual(
            value.monetary_value,
            Decimal("0.0000"),
        )

    def test_unique_monetary_value_constraint(self):
        MonetaryValue.objects.create(
            generic_item=self.generic_item,
            source_file=self.source_file,
            monetary_value=Decimal("35.1234"),
            unit=self.unit,
            classification=CUSTO,
            group=MAODEOBRA,
            type_system=ONERADO,
        )

        with self.assertRaises(IntegrityError):
            MonetaryValue.objects.create(
                generic_item=self.generic_item,
                source_file=self.source_file,
                monetary_value=Decimal("40.0000"),
                unit=self.unit,
                classification=CUSTO,
                group=MAODEOBRA,
                type_system=ONERADO,
            )

    def test_same_item_can_have_different_values_in_different_source_files(self):
        source_1 = self.source_file

        source_2 = create_source_file(
            data_base=DATA_BASE_2024_01,
        )

        value_1 = MonetaryValue.objects.create(
            generic_item=self.generic_item,
            source_file=source_1,
            monetary_value=Decimal("35.0000"),
            unit=self.unit,
            classification=CUSTO,
            group=MAODEOBRA,
            type_system=ONERADO,
        )

        value_2 = MonetaryValue.objects.create(
            generic_item=self.generic_item,
            source_file=source_2,
            monetary_value=Decimal("42.0000"),
            unit=self.unit,
            classification=CUSTO,
            group=MAODEOBRA,
            type_system=ONERADO,
        )

        self.assertNotEqual(
            value_1.monetary_value,
            value_2.monetary_value,
        )

        self.assertEqual(
            value_1.source_file,
            source_1,
        )

        self.assertEqual(
            value_2.source_file,
            source_2,
        )

    def test_same_item_can_have_cost_and_price_in_same_source_file(self):
        cost = MonetaryValue.objects.create(
            generic_item=self.generic_item,
            source_file=self.source_file,
            monetary_value=Decimal("35.0000"),
            unit=self.unit,
            classification=CUSTO,
            group=MAODEOBRA,
            type_system=ONERADO,
        )

        price = MonetaryValue.objects.create(
            generic_item=self.generic_item,
            source_file=self.source_file,
            monetary_value=Decimal("50.0000"),
            unit=self.unit,
            classification=PRECO,
            group=MAODEOBRA,
            type_system=ONERADO,
        )

        self.assertNotEqual(
            cost.pk,
            price.pk,
        )

        self.assertEqual(cost.classification, CUSTO)
        self.assertEqual(price.classification, PRECO)


# ============================================================================
# COMPOSITION
# ============================================================================

class CompositionModelTests(TestCase):
    """Testes do Model Composition."""

    def setUp(self):
        self.source_file = create_source_file(
            methodology=SICRO,
            data_base=DATA_BASE_2023_07,
            type_file=ANALITICO,
        )

        self.generic_item = create_generic_item(
            code="00000001",
        )

        self.generic_description = create_generic_description(
            description="Composição de teste",
            group=COMPOSICAO,
        )

        self.unit = create_unit(
            unit="dm2",
            dimensional="área",
        )

    def create_composition(self):
        composition = Composition.objects.create(
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            fic=Decimal("0.02000"),
            production=Decimal("10.00000"),
            composition_group="11",
        )

        composition.source_files.add(
            self.source_file,
        )

        return composition

    def test_create_composition(self):
        composition = self.create_composition()

        self.assertIsNotNone(composition.pk)
        self.assertEqual(
            composition.generic_item,
            self.generic_item,
        )
        self.assertEqual(
            composition.generic_description,
            self.generic_description,
        )
        self.assertEqual(
            composition.unit,
            self.unit,
        )
        self.assertEqual(
            composition.fic,
            Decimal("0.02000"),
        )
        self.assertEqual(
            composition.production,
            Decimal("10.00000"),
        )
        self.assertEqual(
            composition.composition_group,
            "11",
        )

    def test_str(self):
        composition = self.create_composition()

        expected = (
            f"{composition.generic_item} - "
            f"{composition.generic_description}"
        )

        self.assertEqual(
            str(composition),
            expected,
        )

    def test_composition_can_be_related_to_source_file(self):
        composition = self.create_composition()

        self.assertIn(
            self.source_file,
            composition.source_files.all(),
        )

    def test_unique_composition_constraint(self):
        self.create_composition()

        with self.assertRaises(IntegrityError):
            Composition.objects.create(
                generic_item=self.generic_item,
                generic_description=self.generic_description,
                unit=self.unit,
                fic=Decimal("0.02000"),
                production=Decimal("10.00000"),
                composition_group="11",
            )

    def test_different_production_allows_different_composition(self):
        composition_1 = self.create_composition()

        composition_2 = Composition.objects.create(
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            fic=Decimal("0.02000"),
            production=Decimal("20.00000"),
            composition_group="11",
        )

        self.assertNotEqual(
            composition_1.pk,
            composition_2.pk,
        )

    def test_different_fic_allows_different_composition(self):
        composition_1 = self.create_composition()

        composition_2 = Composition.objects.create(
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            fic=Decimal("0.03000"),
            production=Decimal("10.00000"),
            composition_group="11",
        )

        self.assertNotEqual(
            composition_1.pk,
            composition_2.pk,
        )

    def test_reverse_relationships_exist(self):
        composition = self.create_composition()

        self.assertEqual(
            self.generic_item.compositions.count(),
            1,
        )

        self.assertEqual(
            self.generic_description.compositions.count(),
            1,
        )

        self.assertEqual(
            self.unit.compositions.count(),
            1,
        )

        self.assertEqual(
            self.source_file.compositions.count(),
            1,
        )


# ============================================================================
# EQUIPMENT ITEM
# ============================================================================

class EquipmentItemModelTests(TestCase):
    """Testes do Model EquipmentItem."""

    def setUp(self):
        self.composition = create_composition(
            code="COMP001",
            description="Composição com equipamento",
        )

        self.generic_item = create_generic_item(
            code="EQ001",
        )

        self.generic_description = create_generic_description(
            description="Escavadeira hidráulica",
            group=EQUIPAMENTO,
        )

        self.unit = create_unit(
            unit="h",
            dimensional=None,
        )

        self.source_file = self.composition.source_files.first()

    def test_create_equipment_item(self):
        item = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.50000"),
            input_use=Decimal("0.75000"),
            input_group=EQUIPAMENTO,
        )

        item.source_files.add(
            self.source_file,
        )

        self.assertIsNotNone(item.pk)
        self.assertEqual(
            item.input_quantity,
            Decimal("1.50000"),
        )
        self.assertEqual(
            item.input_use,
            Decimal("0.75000"),
        )

    def test_str(self):
        item = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.50000"),
            input_use=Decimal("0.75000"),
            input_group=EQUIPAMENTO,
        )

        expected = (
            f"{self.composition.generic_item.code} - "
            f"{self.generic_item} - "
            f"{self.generic_description}"
        )

        self.assertEqual(
            str(item),
            expected,
        )

    def test_input_use_can_be_null(self):
        item = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.50000"),
            input_use=None,
            input_group=EQUIPAMENTO,
        )

        self.assertIsNone(
            item.input_use,
        )

    def test_unique_equipment_constraint(self):
        EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.50000"),
            input_use=Decimal("0.75000"),
            input_group=EQUIPAMENTO,
        )

        with self.assertRaises(IntegrityError):
            EquipmentItem.objects.create(
                composition=self.composition,
                generic_item=self.generic_item,
                generic_description=self.generic_description,
                unit=self.unit,
                input_quantity=Decimal("1.50000"),
                input_use=Decimal("0.75000"),
                input_group=EQUIPAMENTO,
            )

    def test_different_input_use_allows_different_equipment_item(self):
        item_1 = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.50000"),
            input_use=Decimal("0.75000"),
            input_group=EQUIPAMENTO,
        )

        item_2 = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.50000"),
            input_use=Decimal("0.85000"),
            input_group=EQUIPAMENTO,
        )

        self.assertNotEqual(
            item_1.pk,
            item_2.pk,
        )


# ============================================================================
# WORKMAN ITEM
# ============================================================================

class WorkmanItemModelTests(TestCase):
    """Testes do Model WorkmanItem."""

    def setUp(self):
        self.composition = create_composition(
            code="COMP002",
            description="Composição com mão de obra",
        )

        self.generic_item = create_generic_item(
            code="MO001",
        )

        self.generic_description = create_generic_description(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        self.unit = create_unit(
            unit="h",
            dimensional=None,
        )

    def test_create_workman_item(self):
        item = WorkmanItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("2.50000"),
            input_group=MAODEOBRA,
        )

        self.assertIsNotNone(item.pk)
        self.assertEqual(
            item.input_quantity,
            Decimal("2.50000"),
        )

    def test_str(self):
        item = WorkmanItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("2.50000"),
            input_group=MAODEOBRA,
        )

        expected = (
            f"{self.composition.generic_item.code} - "
            f"{self.generic_item} - "
            f"{self.generic_description}"
        )

        self.assertEqual(
            str(item),
            expected,
        )

    def test_unique_workman_constraint(self):
        WorkmanItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("2.50000"),
            input_group=MAODEOBRA,
        )

        with self.assertRaises(IntegrityError):
            WorkmanItem.objects.create(
                composition=self.composition,
                generic_item=self.generic_item,
                generic_description=self.generic_description,
                unit=self.unit,
                input_quantity=Decimal("2.50000"),
                input_group=MAODEOBRA,
            )

    def test_different_quantity_allows_different_workman_item(self):
        item_1 = WorkmanItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("2.50000"),
            input_group=MAODEOBRA,
        )

        item_2 = WorkmanItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("3.50000"),
            input_group=MAODEOBRA,
        )

        self.assertNotEqual(
            item_1.pk,
            item_2.pk,
        )


# ============================================================================
# MATERIAL ITEM
# ============================================================================

class MaterialItemModelTests(TestCase):
    """Testes do Model MaterialItem."""

    def setUp(self):
        self.composition = create_composition(
            code="COMP003",
            description="Composição com material",
        )

        self.generic_item = create_generic_item(
            code="MAT001",
        )

        self.generic_description = create_generic_description(
            description="Cimento Portland",
            group=MATERIAL,
        )

        self.unit = create_unit(
            unit="kg",
        )

    def test_create_material_item(self):
        item = MaterialItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("350.00000"),
            input_group=MATERIAL,
        )

        self.assertIsNotNone(item.pk)
        self.assertEqual(
            item.input_quantity,
            Decimal("350.00000"),
        )

    def test_str(self):
        item = MaterialItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("350.00000"),
            input_group=MATERIAL,
        )

        expected = (
            f"{self.composition.generic_item.code} - "
            f"{self.generic_item} - "
            f"{self.generic_description}"
        )

        self.assertEqual(
            str(item),
            expected,
        )

    def test_unique_material_constraint(self):
        MaterialItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("350.00000"),
            input_group=MATERIAL,
        )

        with self.assertRaises(IntegrityError):
            MaterialItem.objects.create(
                composition=self.composition,
                generic_item=self.generic_item,
                generic_description=self.generic_description,
                unit=self.unit,
                input_quantity=Decimal("350.00000"),
                input_group=MATERIAL,
            )

    def test_different_quantity_allows_different_material_item(self):
        item_1 = MaterialItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("350.00000"),
            input_group=MATERIAL,
        )

        item_2 = MaterialItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("400.00000"),
            input_group=MATERIAL,
        )

        self.assertNotEqual(
            item_1.pk,
            item_2.pk,
        )


# ============================================================================
# AUXILIARY ACTIVITY ITEM
# ============================================================================

class AuxiliaryActivityItemModelTests(TestCase):
    """Testes do Model AuxiliaryActivityItem."""

    def setUp(self):
        self.composition = create_composition(
            code="COMP004",
            description="Composição com atividade auxiliar",
        )

        self.generic_item = create_generic_item(
            code="AUX001",
        )

        self.generic_description = create_generic_description(
            description="Atividade auxiliar de teste",
            group=COMPOSICAO,
        )

        self.unit = create_unit(
            unit="m",
            dimensional=None
        )


    def test_create_auxiliary_activity_item(self):
        item = AuxiliaryActivityItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.25000"),
            input_group=AUXILIAR,
        )

        self.assertIsNotNone(item.pk)
        self.assertEqual(
            item.input_quantity,
            Decimal("1.25000"),
        )
        self.assertEqual(
            item.input_group,
            AUXILIAR,
        )

    def test_str(self):
        item = AuxiliaryActivityItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.25000"),
            input_group=AUXILIAR,
        )

        expected = (
            f"{self.composition.generic_item.code} - "
            f"{self.generic_item} - "
            f"{self.generic_description}"
        )

        self.assertEqual(
            str(item),
            expected,
        )

    def test_unique_activity_constraint(self):
        AuxiliaryActivityItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.25000"),
            input_group=AUXILIAR,
        )

        with self.assertRaises(IntegrityError):
            AuxiliaryActivityItem.objects.create(
                composition=self.composition,
                generic_item=self.generic_item,
                generic_description=self.generic_description,
                unit=self.unit,
                input_quantity=Decimal("1.25000"),
                input_group=AUXILIAR,
            )

    def test_different_quantity_allows_different_activity(self):
        item_1 = AuxiliaryActivityItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("1.25000"),
            input_group=AUXILIAR,
        )

        item_2 = AuxiliaryActivityItem.objects.create(
            composition=self.composition,
            generic_item=self.generic_item,
            generic_description=self.generic_description,
            unit=self.unit,
            input_quantity=Decimal("2.50000"),
            input_group=AUXILIAR,
        )

        self.assertNotEqual(
            item_1.pk,
            item_2.pk,
        )


# ============================================================================
# TRANSPORT ITEM
# ============================================================================

class TransportItemModelTests(TestCase):
    """Testes do Model TransportItem."""

    def setUp(self):
        self.composition = create_composition(
            code="COMP005",
            description="Composição com transporte",
        )

        self.transport_generic_item = create_generic_item(
            code="TR001",
        )

        self.transport_description = create_generic_description(
            description="Transporte de material",
            group=MATERIAL,
        )

        self.proprietary_item = create_generic_item(
            code="PROP001",
        )

        self.unit = create_unit(
            unit="t",
        )

    def test_create_transport_item(self):
        item = TransportItem.objects.create(
            composition=self.composition,
            generic_item=self.transport_generic_item,
            generic_description=self.transport_description,
            unit=self.unit,
            input_quantity=Decimal("12.50000"),
            input_group=MATERIAL,
            proprietary_item=self.proprietary_item,
        )

        self.assertIsNotNone(item.pk)
        self.assertEqual(
            item.input_quantity,
            Decimal("12.50000"),
        )
        self.assertEqual(
            item.proprietary_item,
            self.proprietary_item,
        )

    def test_str(self):
        item = TransportItem.objects.create(
            composition=self.composition,
            generic_item=self.transport_generic_item,
            generic_description=self.transport_description,
            unit=self.unit,
            input_quantity=Decimal("12.50000"),
            input_group=MATERIAL,
            proprietary_item=self.proprietary_item,
        )

        expected = (
            f"{self.composition.generic_item.code} - "
            f"{self.transport_generic_item} - "
            f"{self.transport_description}"
        )

        self.assertEqual(
            str(item),
            expected,
        )

    def test_proprietary_item_can_be_null(self):
        item = TransportItem.objects.create(
            composition=self.composition,
            generic_item=self.transport_generic_item,
            generic_description=self.transport_description,
            unit=self.unit,
            input_quantity=Decimal("12.50000"),
            input_group=MATERIAL,
            proprietary_item=None,
        )

        self.assertIsNone(
            item.proprietary_item,
        )

    def test_unique_transport_constraint(self):
        TransportItem.objects.create(
            composition=self.composition,
            generic_item=self.transport_generic_item,
            generic_description=self.transport_description,
            unit=self.unit,
            input_quantity=Decimal("12.50000"),
            input_group=MATERIAL,
            proprietary_item=self.proprietary_item,
        )

        with self.assertRaises(IntegrityError):
            TransportItem.objects.create(
                composition=self.composition,
                generic_item=self.transport_generic_item,
                generic_description=self.transport_description,
                unit=self.unit,
                input_quantity=Decimal("12.50000"),
                input_group=MATERIAL,
                proprietary_item=self.proprietary_item,
            )

    def test_different_proprietary_item_allows_different_transport(self):
        proprietary_2 = create_generic_item(
            code="PROP002",
        )

        item_1 = TransportItem.objects.create(
            composition=self.composition,
            generic_item=self.transport_generic_item,
            generic_description=self.transport_description,
            unit=self.unit,
            input_quantity=Decimal("12.50000"),
            input_group=MATERIAL,
            proprietary_item=self.proprietary_item,
        )

        item_2 = TransportItem.objects.create(
            composition=self.composition,
            generic_item=self.transport_generic_item,
            generic_description=self.transport_description,
            unit=self.unit,
            input_quantity=Decimal("12.50000"),
            input_group=MATERIAL,
            proprietary_item=proprietary_2,
        )

        self.assertNotEqual(
            item_1.pk,
            item_2.pk,
        )


# ============================================================================
# INTEGRAÇÃO ENTRE OS MODELS
# ============================================================================

class ModelsIntegrationTests(TestCase):
    """
    Testes que verificam a estrutura conjunta dos Models.

    Estes testes são importantes porque o sistema não representa somente
    objetos isolados: ele representa uma base de composições vinculada a
    uma determinada fonte/data-base.
    """

    def test_complete_composition_structure(self):
        """
        Cria uma composição contendo:

            - equipamento
            - mão de obra
            - material
            - atividade auxiliar
            - transporte

        e verifica se todos os relacionamentos estão funcionando.
        """

        source_file = create_source_file(
            methodology=SICRO,
            data_base=DATA_BASE_2023_07,
            uf=GOIAS,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        composition = create_composition(
            code="COMP100",
            description="Composição completa",
            source_file=source_file,
        )

        # ------------------------------------------------------------------
        # Equipamento
        # ------------------------------------------------------------------

        equipment_item = create_generic_item(
            code="EQ100",
        )

        equipment_description = create_generic_description(
            description="Equipamento da composição",
            group=EQUIPAMENTO,
        )

        equipment_unit = create_unit(
            unit="dia",
            dimensional=None,
        )

        equipment = EquipmentItem.objects.create(
            composition=composition,
            generic_item=equipment_item,
            generic_description=equipment_description,
            unit=equipment_unit,
            input_quantity=Decimal("1.00000"),
            input_use=Decimal("0.80000"),
            input_group=EQUIPAMENTO,
        )

        equipment.source_files.add(source_file)

        # ------------------------------------------------------------------
        # Mão de obra
        # ------------------------------------------------------------------

        workman_item = create_generic_item(
            code="MO100",
        )

        workman_description = create_generic_description(
            description="Mão de obra da composição",
            group=MAODEOBRA,
        )

        workman_unit = create_unit(
            unit="mês",
            dimensional=None,
        )

        workman = WorkmanItem.objects.create(
            composition=composition,
            generic_item=workman_item,
            generic_description=workman_description,
            unit=workman_unit,
            input_quantity=Decimal("2.00000"),
            input_group=MAODEOBRA,
        )

        workman.source_files.add(source_file)

        # ------------------------------------------------------------------
        # Material
        # ------------------------------------------------------------------

        material_item = create_generic_item(
            code="MAT100",
        )

        material_description = create_generic_description(
            description="Material da composição",
            group=MATERIAL,
        )

        material_unit = create_unit(
            unit="l",
        )

        material = MaterialItem.objects.create(
            composition=composition,
            generic_item=material_item,
            generic_description=material_description,
            unit=material_unit,
            input_quantity=Decimal("10.00000"),
            input_group=MATERIAL,
        )

        material.source_files.add(source_file)

        # ------------------------------------------------------------------
        # Atividade auxiliar
        # ------------------------------------------------------------------

        auxiliary_item = create_generic_item(
            code="AX100",
        )

        auxiliary_description = create_generic_description(
            description="Atividade auxiliar da composição",
            group=COMPOSICAO,
        )

        auxiliary_unit = create_unit(
            unit="dm",
        )

        auxiliary = AuxiliaryActivityItem.objects.create(
            composition=composition,
            generic_item=auxiliary_item,
            generic_description=auxiliary_description,
            unit=auxiliary_unit,
            input_quantity=Decimal("0.50000"),
            input_group=AUXILIAR,
        )

        auxiliary.source_files.add(source_file)

        # ------------------------------------------------------------------
        # Transporte
        # ------------------------------------------------------------------

        transport_item = create_generic_item(
            code="TR100",
        )

        transport_description = create_generic_description(
            description="Transporte da composição",
            group=MATERIAL,
        )

        transport_unit = create_unit(
            unit="tkm",
        )

        proprietary_item = create_generic_item(
            code="PROP100",
        )

        transport = TransportItem.objects.create(
            composition=composition,
            generic_item=transport_item,
            generic_description=transport_description,
            unit=transport_unit,
            input_quantity=Decimal("5.00000"),
            input_group=MATERIAL,
            proprietary_item=proprietary_item,
        )

        transport.source_files.add(source_file)

        # ------------------------------------------------------------------
        # Verificações
        # ------------------------------------------------------------------

        self.assertEqual(
            composition.equipments.count(),
            1,
        )

        self.assertEqual(
            composition.workmen.count(),
            1,
        )

        self.assertEqual(
            composition.materials.count(),
            1,
        )

        self.assertEqual(
            composition.activities.count(),
            1,
        )

        self.assertEqual(
            composition.transports.count(),
            1,
        )

        self.assertEqual(
            equipment.composition,
            composition,
        )

        self.assertEqual(
            workman.composition,
            composition,
        )

        self.assertEqual(
            material.composition,
            composition,
        )

        self.assertEqual(
            auxiliary.composition,
            composition,
        )

        self.assertEqual(
            transport.composition,
            composition,
        )

    def test_same_description_can_represent_different_codes(self):
        """
        Teste fundamental para a particularidade das bases.

        Dois códigos diferentes podem compartilhar exatamente a mesma
        descrição.

        Exemplo:

            Código 1 -> "Brita"
            Código 2 -> "Brita"

        O sistema não deve precisar duplicar GenericDescription.
        """

        description = create_generic_description(
            description="Brita",
            group=MATERIAL,
        )

        item_1 = create_generic_item(
            code="MAT201",
        )

        item_2 = create_generic_item(
            code="MAT202",
        )

        description.generic_items.add(
            item_1,
            item_2,
        )

        self.assertEqual(
            description.generic_items.count(),
            2,
        )

        self.assertEqual(
            item_1.descriptions.first(),
            description,
        )

        self.assertEqual(
            item_2.descriptions.first(),
            description,
        )

    def test_same_item_has_different_values_by_source_file(self):
        """
        Teste histórico:

        O mesmo GenericItem pode possuir valores diferentes em
        diferentes data-bases.
        """

        source_2023 = create_source_file(
            methodology=SICRO,
            data_base=DATA_BASE_2023_07,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        source_2024 = create_source_file(
            methodology=SICRO,
            data_base=DATA_BASE_2024_01,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        item = create_generic_item(
            code="MAT300",
        )

        unit = create_unit(
            unit="dm3",
        )

        value_2023 = MonetaryValue.objects.create(
            generic_item=item,
            source_file=source_2023,
            monetary_value=Decimal("1.2500"),
            unit=unit,
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

        value_2024 = MonetaryValue.objects.create(
            generic_item=item,
            source_file=source_2024,
            monetary_value=Decimal("1.8500"),
            unit=unit,
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

        self.assertEqual(
            item.values.count(),
            2,
        )

        self.assertEqual(
            value_2023.monetary_value,
            Decimal("1.2500"),
        )

        self.assertEqual(
            value_2024.monetary_value,
            Decimal("1.8500"),
        )

        self.assertNotEqual(
            value_2023.monetary_value,
            value_2024.monetary_value,
        )

    def test_same_composition_can_be_related_to_multiple_source_files(self):
        """
        Verifica a relação ManyToMany entre Composition e SourceFile.

        Isso é importante para a estratégia de armazenamento adotada
        pelo projeto.
        """

        source_2023 = create_source_file(
            methodology=SICRO,
            data_base=DATA_BASE_2023_07,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        source_2024 = create_source_file(
            methodology=SICRO,
            data_base=DATA_BASE_2024_01,
            type_system=ONERADO,
            type_file=ANALITICO,
        )

        composition = create_composition(
            code="COMP400",
            description="Composição reutilizada",
            source_file=source_2023,
        )

        composition.source_files.add(
            source_2024,
        )

        self.assertEqual(
            composition.source_files.count(),
            2,
        )

        self.assertIn(
            source_2023,
            composition.source_files.all(),
        )

        self.assertIn(
            source_2024,
            composition.source_files.all(),
        )