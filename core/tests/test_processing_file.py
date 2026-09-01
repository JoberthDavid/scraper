"""
Testes do processamento de arquivos XLSX.

Arquivo testado:
    core/usefuls/processing_file.py

Objetivo:
    Garantir que a transformação dos DataFrames provenientes dos XLSX
    preserve corretamente a estrutura de dados da API.

IMPORTANTE:

    Estes testes NÃO alteram os Models existentes.

    Eles documentam o comportamento esperado do processamento atual,
    especialmente:

        - criação de Unit;
        - criação de GenericItem;
        - criação de GenericDescription;
        - relacionamento com SourceFile;
        - relacionamento entre GenericItem e GenericDescription;
        - criação de MonetaryValue;
        - diferenciação de custo/preço;
        - diferenciação de custo produtivo/improdutivo;
        - processamento de composição;
        - processamento de insumos de composição.

Executar:

    python manage.py test core.tests_processing_file
"""

from datetime import date
from decimal import Decimal
from io import BytesIO

import pandas as pd

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
    AUXILIAR,
    TEMPO_FIXO,
    LEITO_NATURAL,
    REVESTIMENTO_PRIMARIO,
    PAVIMENTADO,
    FERROVIARIO,
)

from core.usefuls.data_structure import (
    df_code,
    df_description,
    df_unit,
    df_monetary_value,
    df_purchase_value,
    df_deprecation,
    df_equity_opportunity,
    df_insurance_and_taxes,
    df_maintenance,
    df_operation,
    df_labor,
    df_productive_cost,
    df_unproductive_cost,
    df_wage,
    df_charges,
    df_unhealthy,
    df_quantity,
    df_productive_use,
    df_unproductive_use,
    df_production,
)

from core.usefuls.processing_file import (
    FileXlsxPreparer,
    UnitPreparer,
    MonetaryValuePreparer,
    GenericItemPreparer,
    GenericDescriptionPreparer,
    SourceFilePreparer,
    BasicDataCompositionPreparer,
    AllocationPreparer,
    FileXlsxProcessor,
)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def create_source_file(
    *,
    data_base=date(2023, 7, 1),
    type_file=MATERIAL,
    type_system=ONERADO,
    methodology=SICRO,
    uf=GOIAS,
):
    """
    Cria um SourceFile para os testes.

    O arquivo físico não é necessário para os testes do processamento,
    porque trabalhamos diretamente com DataFrames.
    """

    return SourceFile.objects.create(
        data_base=data_base,
        source_file="teste.xlsx",
        type_file=type_file,
        type_system=type_system,
        methodology=methodology,
        uf=uf,
    )


# ============================================================================
# FILE XLSX PREPARER
# ============================================================================

class FileXlsxPreparerTests(TestCase):
    """
    Testes da preparação do DataFrame antes do processamento dos Models.
    """

    def create_excel_response(self, dataframe, header=False):
        """
        Constrói uma resposta semelhante ao objeto esperado pelo código:

            response[df_body].read()

        utilizando um XLSX real criado em memória.
        """

        from core.usefuls.data_structure import df_body

        buffer = BytesIO()

        dataframe.to_excel(
            buffer,
            index=False,
            header=header,
        )

        buffer.seek(0)

        return {
            df_body: buffer,
        }

    def test_prepare_material_dataframe(self):
        """
        MATERIAL:

            código
            descrição
            unidade
            valor

        deve ser convertido para o DataFrame esperado.
        """

        source_file = create_source_file(
            type_file=MATERIAL,
        )

        original = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Areia", "m3", 80.00],
            ]
        )

        response = self.create_excel_response(original)

        preparer = FileXlsxPreparer()

        dataframe = preparer.get_data_frame_prepared(
            response=response,
            type_file=MATERIAL,
            source_file=source_file,
        )

        self.assertEqual(
            len(dataframe),
            2,
        )

        self.assertEqual(
            dataframe.iloc[0][df_code],
            "M1001",
        )

        self.assertEqual(
            dataframe.iloc[0][df_description],
            "Cimento",
        )

        self.assertEqual(
            dataframe.iloc[0][df_unit],
            "kg",
        )

        self.assertAlmostEqual(
            float(dataframe.iloc[0][df_monetary_value]),
            1.25,
            places=4,
        )


    def test_prepare_material_replaces_dash_by_zero(self):
        """
        O processamento atual converte '-' em 0.0 para valores monetários
        de MATERIAL.
        """

        source_file = create_source_file(
            type_file=MATERIAL,
        )

        original = pd.DataFrame(
            [
                ["M1001", "Material sem preço", "kg", "-"],
            ]
        )

        response = self.create_excel_response(original)

        preparer = FileXlsxPreparer()

        dataframe = preparer.get_data_frame_prepared(
            response=response,
            type_file=MATERIAL,
            source_file=source_file,
        )

        self.assertEqual(
            float(dataframe.iloc[0][df_monetary_value]),
            0.0,
        )

    def test_prepare_equipment_dataframe_creates_hour_unit(self):
        """
        Para EQUIPAMENTO, o código atual força:

            unit = "h"
        """

        source_file = create_source_file(
            type_file=EQUIPAMENTO,
        )

        original = pd.DataFrame(
            [
                [
                    "E1001",
                    "Escavadeira",
                    100000,
                    0.10,
                    0.05,
                    0.01,
                    0.15,
                    0.20,
                    0.10,
                    100.00,
                    80.00,
                ],
            ]
        )

        response = self.create_excel_response(original)

        preparer = FileXlsxPreparer()

        dataframe = preparer.get_data_frame_prepared(
            response=response,
            type_file=EQUIPAMENTO,
            source_file=source_file,
        )

        self.assertEqual(
            dataframe.iloc[0][df_code],
            "E1001",
        )

        self.assertEqual(
            dataframe.iloc[0][df_description],
            "Escavadeira",
        )

        self.assertEqual(
            dataframe.iloc[0][df_unit],
            "h",
        )

        self.assertAlmostEqual(
            float(dataframe.iloc[0][df_productive_cost]),
            100.00,
            places=2,
        )

        self.assertAlmostEqual(
            float(dataframe.iloc[0][df_unproductive_cost]),
            80.00,
            places=2,
        )

    def test_prepare_sintetico_dataframe(self):
        """
        Testa a leitura da estrutura SINTÉTICA.
        """

        source_file = create_source_file(
            type_file=SINTETICO,
        )

        original = pd.DataFrame(
            [
                [
                    "1100001",
                    "Execução de serviço",
                    "m3",
                    125.50,
                ],
            ]
        )

        response = self.create_excel_response(original)

        preparer = FileXlsxPreparer()

        dataframe = preparer.get_data_frame_prepared(
            response=response,
            type_file=SINTETICO,
            source_file=source_file,
        )

        self.assertEqual(
            dataframe.iloc[0][df_code],
            "1100001",
        )

        self.assertEqual(
            dataframe.iloc[0][df_description],
            "Execução de serviço",
        )

        self.assertEqual(
            dataframe.iloc[0][df_unit],
            "m3",
        )

        self.assertAlmostEqual(
            float(dataframe.iloc[0][df_monetary_value]),
            125.50,
            places=2,
        )

    def test_prepare_analitico_fills_missing_production_with_zero(self):
        """
        O código atual preenche valores ausentes de production com 0.0
        para ANALITICO.
        """

        source_file = create_source_file(
            type_file=ANALITICO,
        )

        original = pd.DataFrame(
            [
                [
                    "COMP001",
                    "Composição",
                    1.0,
                    0.5,
                    0.2,
                    10.0,
                    8.0,
                    None,
                    "m3",
                ],
            ]
        )

        response = self.create_excel_response(
            original,
            header=True,
        )

        preparer = FileXlsxPreparer()

        dataframe = preparer.get_data_frame_prepared(
            response=response,
            type_file=ANALITICO,
            source_file=source_file,
        )

        self.assertEqual(
            float(dataframe.iloc[0][df_production]),
            0.0,
        )


# ============================================================================
# UNIT PREPARER
# ============================================================================

class UnitPreparerTests(TestCase):

    def test_creates_units(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Areia", "m3", 80.00],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        UnitPreparer(
            data_frame=dataframe,
        )

        self.assertEqual(
            Unit.objects.count(),
            2,
        )

        self.assertTrue(
            Unit.objects.filter(unit="kg").exists()
        )

        self.assertTrue(
            Unit.objects.filter(unit="m3").exists()
        )

    def test_does_not_duplicate_existing_unit(self):
        Unit.objects.create(
            unit="kg",
        )

        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Areia", "kg", 80.00],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        UnitPreparer(
            data_frame=dataframe,
        )

        self.assertEqual(
            Unit.objects.filter(unit="kg").count(),
            1,
        )

    def test_get_collection_of_unit(self):
        Unit.objects.create(
            unit="kg",
        )

        Unit.objects.create(
            unit="m3",
        )

        collection = UnitPreparer.get_collection_of_unit()

        self.assertIn(
            "kg",
            collection,
        )

        self.assertIn(
            "m3",
            collection,
        )

        self.assertEqual(
            collection["kg"].unit,
            "kg",
        )


# ============================================================================
# GENERIC ITEM PREPARER
# ============================================================================

class GenericItemPreparerTests(TestCase):

    def test_creates_generic_items(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Areia", "m3", 80.00],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        GenericItemPreparer(
            data_frame=dataframe,
        )

        self.assertEqual(
            GenericItem.objects.count(),
            2,
        )

        self.assertTrue(
            GenericItem.objects.filter(code="M1001").exists()
        )

        self.assertTrue(
            GenericItem.objects.filter(code="M1002").exists()
        )

    def test_does_not_duplicate_existing_generic_item(self):
        GenericItem.objects.create(
            code="M1001",
        )

        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        GenericItemPreparer(
            data_frame=dataframe,
        )

        self.assertEqual(
            GenericItem.objects.filter(
                code="M1001"
            ).count(),
            1,
        )

    def test_get_collection_of_generic_item_unrelated(self):
        item = GenericItem.objects.create(
            code="M1001",
        )

        preparer = GenericItemPreparer.__new__(
            GenericItemPreparer
        )

        collection = (
            preparer
            .get_collection_of_generic_item_unrelated()
        )

        self.assertIn(
            "M1001",
            collection,
        )

        self.assertEqual(
            collection["M1001"].pk,
            item.pk,
        )


# ============================================================================
# GENERIC DESCRIPTION PREPARER
# ============================================================================

class GenericDescriptionPreparerTests(TestCase):

    def test_creates_material_descriptions_with_material_group(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        GenericDescriptionPreparer(
            data_frame=dataframe,
            type_file=MATERIAL,
        )

        description = GenericDescription.objects.get(
            description="Cimento"
        )

        self.assertEqual(
            description.group,
            MATERIAL,
        )

    def test_sintetico_uses_composition_group(self):
        dataframe = pd.DataFrame(
            [
                ["110001", "Composição", "m3", 125.50],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        GenericDescriptionPreparer(
            data_frame=dataframe,
            type_file=SINTETICO,
        )

        description = GenericDescription.objects.get(
            description="Composição"
        )

        self.assertEqual(
            description.group,
            COMPOSICAO,
        )

    def test_does_not_duplicate_same_description(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Cimento", "kg", 1.30],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        GenericDescriptionPreparer(
            data_frame=dataframe,
            type_file=MATERIAL,
        )

        self.assertEqual(
            GenericDescription.objects.filter(
                description="Cimento"
            ).count(),
            1,
        )

    def test_get_collection_of_generic_description_unrelated(self):
        description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        preparer = GenericDescriptionPreparer.__new__(
            GenericDescriptionPreparer
        )

        collection = (
            preparer
            .get_collection_of_generic_description_unrelated()
        )

        self.assertIn(
            "Cimento",
            collection,
        )

        self.assertEqual(
            collection["Cimento"].pk,
            description.pk,
        )


# ============================================================================
# SOURCE FILE PREPARER
# ============================================================================

class SourceFilePreparerTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file(
            type_file=MATERIAL,
        )

        self.dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Areia", "m3", 80.00],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        GenericItemPreparer(
            data_frame=self.dataframe
        )

        GenericDescriptionPreparer(
            data_frame=self.dataframe,
            type_file=MATERIAL,
        )

        self.items = (
            GenericItemPreparer.__new__(
                GenericItemPreparer
            )
            .get_collection_of_generic_item_unrelated()
        )

        self.descriptions = (
            GenericDescriptionPreparer.__new__(
                GenericDescriptionPreparer
            )
            .get_collection_of_generic_description_unrelated()
        )

    def test_relates_items_to_source_file(self):
        SourceFilePreparer(
            data_frame=self.dataframe,
            unrelated_items=self.items,
            unrelated_descriptions=self.descriptions,
            source_file=self.source_file,
        )

        item = GenericItem.objects.get(
            code="M1001"
        )

        self.assertIn(
            self.source_file,
            item.source_files.all(),
        )

    def test_relates_descriptions_to_source_file(self):
        SourceFilePreparer(
            data_frame=self.dataframe,
            unrelated_items=self.items,
            unrelated_descriptions=self.descriptions,
            source_file=self.source_file,
        )

        description = GenericDescription.objects.get(
            description="Cimento"
        )

        self.assertIn(
            self.source_file,
            description.source_files.all(),
        )

    def test_relates_description_to_item(self):
        SourceFilePreparer(
            data_frame=self.dataframe,
            unrelated_items=self.items,
            unrelated_descriptions=self.descriptions,
            source_file=self.source_file,
        )

        item = GenericItem.objects.get(
            code="M1001"
        )

        description = GenericDescription.objects.get(
            description="Cimento"
        )

        self.assertIn(
            description,
            item.descriptions.all(),
        )

        self.assertIn(
            item,
            description.generic_items.all(),
        )

    def test_same_description_is_shared_by_different_codes(self):
        """
        REGRA FUNDAMENTAL DO PROJETO.

        Dois códigos diferentes podem possuir exatamente a mesma descrição.

        O processamento deve criar:

            M1001 -> Cimento
            M1002 -> Cimento

        usando um único GenericDescription.
        """

        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Cimento", "kg", 1.30],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        GenericItemPreparer(
            data_frame=dataframe
        )

        GenericDescriptionPreparer(
            data_frame=dataframe,
            type_file=MATERIAL,
        )

        items = (
            GenericItemPreparer.__new__(
                GenericItemPreparer
            )
            .get_collection_of_generic_item_unrelated()
        )

        descriptions = (
            GenericDescriptionPreparer.__new__(
                GenericDescriptionPreparer
            )
            .get_collection_of_generic_description_unrelated()
        )

        SourceFilePreparer(
            data_frame=dataframe,
            unrelated_items=items,
            unrelated_descriptions=descriptions,
            source_file=self.source_file,
        )

        self.assertEqual(
            GenericDescription.objects.filter(
                description="Cimento"
            ).count(),
            1,
        )

        description = GenericDescription.objects.get(
            description="Cimento"
        )

        self.assertEqual(
            description.generic_items.count(),
            2,
        )


# ============================================================================
# MONETARY VALUE PREPARER
# ============================================================================

class MonetaryValuePreparerTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file(
            type_file=MATERIAL,
        )

        self.item_1 = GenericItem.objects.create(
            code="M1001",
        )

        self.item_2 = GenericItem.objects.create(
            code="M1002",
        )

        self.unit_kg = Unit.objects.create(
            unit="kg",
        )

        self.unit_m3 = Unit.objects.create(
            unit="m3",
        )

    def test_material_creates_cost_values(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1002", "Areia", "m3", 80.00],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        related_items = {
            "M1001": self.item_1,
            "M1002": self.item_2,
        }

        units = {
            "kg": self.unit_kg,
            "m3": self.unit_m3,
        }

        MonetaryValuePreparer(
            data_frame=dataframe,
            type_file=MATERIAL,
            source_file=self.source_file,
            related_items=related_items,
            units=units,
        )

        self.assertEqual(
            MonetaryValue.objects.count(),
            2,
        )

        value = MonetaryValue.objects.get(
            generic_item=self.item_1
        )

        self.assertEqual(
            value.classification,
            CUSTO,
        )

        self.assertEqual(
            value.group,
            MATERIAL,
        )

        self.assertEqual(
            value.type_system,
            self.source_file.type_system,
        )

        self.assertEqual(
            Decimal(str(value.monetary_value)),
            Decimal("1.25"),
        )

    def test_sintetico_creates_price_values(self):
        source_file = create_source_file(
            type_file=SINTETICO,
        )

        item = GenericItem.objects.create(
            code="110001",
        )

        unit = Unit.objects.get(
            unit="m3",
        )

        dataframe = pd.DataFrame(
            [
                ["110001", "Composição", "m3", 125.50],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        MonetaryValuePreparer(
            data_frame=dataframe,
            type_file=SINTETICO,
            source_file=source_file,
            related_items={
                "110001": item,
            },
            units={
                "m3": unit,
            },
        )

        value = MonetaryValue.objects.get(
            generic_item=item
        )

        self.assertEqual(
            value.classification,
            PRECO,
        )

        self.assertEqual(
            value.group,
            COMPOSICAO,
        )

    def test_equipment_creates_productive_and_unproductive_values(self):
        source_file = create_source_file(
            type_file=EQUIPAMENTO,
        )

        item = GenericItem.objects.create(
            code="E1001",
        )

        unit = Unit.objects.create(
            unit="h",
        )

        dataframe = pd.DataFrame(
            [
                [
                    "E1001",
                    "Escavadeira",
                    100000,
                    0.10,
                    0.05,
                    0.01,
                    0.15,
                    0.20,
                    0.10,
                    100.00,
                    80.00,
                ],
            ],
            columns=[
                df_code,
                df_description,
                df_purchase_value,
                df_deprecation,
                df_equity_opportunity,
                df_insurance_and_taxes,
                df_maintenance,
                df_operation,
                df_labor,
                df_productive_cost,
                df_unproductive_cost,
            ],
        )

        dataframe[df_unit] = "h"

        MonetaryValuePreparer(
            data_frame=dataframe,
            type_file=EQUIPAMENTO,
            source_file=source_file,
            related_items={
                "E1001": item,
            },
            units={
                "h": unit,
            },
        )

        self.assertEqual(
            MonetaryValue.objects.count(),
            2,
        )

        productive = MonetaryValue.objects.get(
            generic_item=item,
            classification=PRODUTIVO,
        )

        unproductive = MonetaryValue.objects.get(
            generic_item=item,
            classification=IMPRODUTIVO,
        )

        self.assertEqual(
            Decimal(str(productive.monetary_value)),
            Decimal("100.0"),
        )

        self.assertEqual(
            Decimal(str(unproductive.monetary_value)),
            Decimal("80.0"),
        )

    def test_same_item_can_have_different_values_by_source_file(self):
        """
        TESTE HISTÓRICO FUNDAMENTAL.

        O mesmo código pode ter valores diferentes em data-bases
        diferentes.
        """

        source_2023 = self.source_file

        source_2024 = create_source_file(
            data_base=date(2024, 1, 1),
            type_file=MATERIAL,
        )

        dataframe_2023 = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        dataframe_2024 = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.85],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        related_items = {
            "M1001": self.item_1,
        }

        units = {
            "kg": self.unit_kg,
        }

        MonetaryValuePreparer(
            data_frame=dataframe_2023,
            type_file=MATERIAL,
            source_file=source_2023,
            related_items=related_items,
            units=units,
        )

        MonetaryValuePreparer(
            data_frame=dataframe_2024,
            type_file=MATERIAL,
            source_file=source_2024,
            related_items=related_items,
            units=units,
        )

        values = MonetaryValue.objects.filter(
            generic_item=self.item_1
        ).order_by(
            "source_file__data_base"
        )

        self.assertEqual(
            values.count(),
            2,
        )

        self.assertEqual(
            Decimal(str(values[0].monetary_value)),
            Decimal("1.25"),
        )

        self.assertEqual(
            Decimal(str(values[1].monetary_value)),
            Decimal("1.85"),
        )


# ============================================================================
# BASIC DATA COMPOSITION PREPARER
# ============================================================================

class BasicDataCompositionPreparerTests(TestCase):

    def setUp(self):

        self.source_file = create_source_file(
            type_file=ANALITICO,
        )

        self.synthetic_source_file = create_source_file(
            type_file=SINTETICO,
        )

        # Unidades
        Unit.objects.create(
            unit="m3",
        )

        # Código da composição
        self.composition_item = GenericItem.objects.create(
            code="1100001",
        )

        # Descrição da composição
        self.composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        self.composition_item.source_files.add(
            self.source_file,
            self.synthetic_source_file,
        )

        self.composition_description.source_files.add(
            self.source_file
        )

    def test_creates_composition_from_analytical_data(self):
        """
        O trecho analítico:

            SISTEMA...
            Custo Unitário de Referência
            Valores em reais (R$)

        deve resultar em uma Composition.
        """

        dataframe = pd.DataFrame(
            [
                [
                    "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS - SICRO",
                    "",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0.10,
                    "m3",
                ],
                [
                    "Custo Unitário de Referência",
                    "",
                    1,
                    0,
                    0,
                    0,
                    0,
                    10.0,
                    "m3",
                ],
                [
                    "1100001",
                    "Execução de concreto",
                    1,
                    0,
                    0,
                    0,
                    0,
                    "Valores em reais (R$)",
                    "m3",
                ],
            ],
            columns=[
                df_code,
                df_description,
                df_quantity,
                df_productive_use,
                df_unproductive_use,
                df_productive_cost,
                df_unproductive_cost,
                df_production,
                df_unit,
            ],
        )

        preparer = BasicDataCompositionPreparer(
            data_frame=dataframe,
            source_file=self.source_file,
        )

        composition = Composition.objects.get(
            generic_item=self.composition_item
        )

        self.assertEqual(
            composition.generic_description,
            self.composition_description,
        )

        self.assertEqual(
            composition.unit.unit,
            "m3",
        )

        self.assertEqual(
            composition.production,
            Decimal("10.00000"),
        )

        self.assertEqual(
            composition.fic,
            Decimal("0.10000"),
        )

        self.assertIn(
            self.source_file,
            composition.source_files.all(),
        )

    def test_composition_group_is_extracted_from_code(self):
        dataframe = pd.DataFrame(
            [
                [
                    "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS - SICRO",
                    "",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0.10,
                    "m3",
                ],
                [
                    "Custo Unitário de Referência",
                    "",
                    1,
                    0,
                    0,
                    0,
                    0,
                    10.0,
                    "m3",
                ],
                [
                    "1100001",
                    "Execução de concreto",
                    1,
                    0,
                    0,
                    0,
                    0,
                    "Valores em reais (R$)",
                    "m3",
                ],
            ],
            columns=[
                df_code,
                df_description,
                df_quantity,
                df_productive_use,
                df_unproductive_use,
                df_productive_cost,
                df_unproductive_cost,
                df_production,
                df_unit,
            ],
        )

        BasicDataCompositionPreparer(
            data_frame=dataframe,
            source_file=self.source_file,
        )

        composition = Composition.objects.get(
            generic_item=self.composition_item
        )

        self.assertEqual(
            composition.composition_group,
            "11",
        )


# ============================================================================
# FILE XLSX PROCESSOR
# ============================================================================

class FileXlsxProcessorTests(TestCase):
    """
    Testes do orquestrador principal.

    Aqui não estamos testando cada detalhe interno novamente.
    Estamos verificando se FileXlsxProcessor chama o fluxo correto
    para cada tipo de arquivo.
    """

    def test_processor_dispatches_material_processing(self):
        source_file = create_source_file(
            type_file=MATERIAL,
        )

        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=MATERIAL,
            source_file=source_file,
        )

        self.assertEqual(
            Unit.objects.count(),
            1,
        )

        self.assertEqual(
            GenericItem.objects.count(),
            1,
        )

        self.assertEqual(
            GenericDescription.objects.count(),
            1,
        )

        self.assertEqual(
            MonetaryValue.objects.count(),
            1,
        )

        item = GenericItem.objects.get(
            code="M1001"
        )

        self.assertIn(
            source_file,
            item.source_files.all(),
        )

        description = GenericDescription.objects.get(
            description="Cimento"
        )

        self.assertIn(
            source_file,
            description.source_files.all(),
        )

        self.assertIn(
            description,
            item.descriptions.all(),
        )

    def test_processor_dispatches_equipment_processing(self):
        source_file = create_source_file(
            type_file=EQUIPAMENTO,
        )

        dataframe = pd.DataFrame(
            [
                [
                    "E1001",
                    "Escavadeira",
                    100000,
                    0.10,
                    0.05,
                    0.01,
                    0.15,
                    0.20,
                    0.10,
                    100.00,
                    80.00,
                ],
            ],
            columns=[
                df_code,
                df_description,
                df_purchase_value,
                df_deprecation,
                df_equity_opportunity,
                df_insurance_and_taxes,
                df_maintenance,
                df_operation,
                df_labor,
                df_productive_cost,
                df_unproductive_cost,
            ],
        )

        dataframe[df_unit] = "h"

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=EQUIPAMENTO,
            source_file=source_file,
        )

        self.assertEqual(
            GenericItem.objects.count(),
            1,
        )

        self.assertEqual(
            MonetaryValue.objects.count(),
            2,
        )

        self.assertTrue(
            MonetaryValue.objects.filter(
                classification=PRODUTIVO
            ).exists()
        )

        self.assertTrue(
            MonetaryValue.objects.filter(
                classification=IMPRODUTIVO
            ).exists()
        )

    def test_processor_dispatches_workman_processing(self):
        source_file = create_source_file(
            type_file=MAODEOBRA,
        )

        dataframe = pd.DataFrame(
            [
                [
                    "P9821",
                    "Pedreiro",
                    "h",
                    20.0,
                    0.0,
                    35.0,
                    0.0,
                ],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_wage,
                df_charges,
                df_monetary_value,
                df_unhealthy,
            ],
        )

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=MAODEOBRA,
            source_file=source_file,
        )

        item = GenericItem.objects.get(
            code="P9821"
        )

        description = GenericDescription.objects.get(
            description="Pedreiro"
        )

        self.assertIn(
            source_file,
            item.source_files.all(),
        )

        self.assertIn(
            source_file,
            description.source_files.all(),
        )

        monetary_value = MonetaryValue.objects.get(
            generic_item=item
        )

        self.assertEqual(
            monetary_value.classification,
            CUSTO,
        )

        self.assertEqual(
            monetary_value.group,
            MAODEOBRA,
        )

    def test_processor_is_idempotent_for_material_data(self):
        """
        Executar o processamento duas vezes com a mesma informação não deve
        duplicar os registros protegidos pelas constraints/ignore_conflicts.
        """

        source_file = create_source_file(
            type_file=MATERIAL,
        )

        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=MATERIAL,
            source_file=source_file,
        )

        first_counts = {
            "units": Unit.objects.count(),
            "items": GenericItem.objects.count(),
            "descriptions": GenericDescription.objects.count(),
            "values": MonetaryValue.objects.count(),
        }

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=MATERIAL,
            source_file=source_file,
        )

        second_counts = {
            "units": Unit.objects.count(),
            "items": GenericItem.objects.count(),
            "descriptions": GenericDescription.objects.count(),
            "values": MonetaryValue.objects.count(),
        }

        self.assertEqual(
            first_counts,
            second_counts,
        )


# ============================================================================
# TESTE DE REGRA HISTÓRICA
# ============================================================================

class HistoricalDataProcessingTests(TestCase):
    """
    Testes que documentam a característica histórica da base.

    O mesmo código pode aparecer em diferentes SourceFiles/data-bases
    e possuir valores diferentes.
    """

    def test_same_code_can_be_processed_in_two_data_bases_with_different_values(self):
        source_2023 = create_source_file(
            data_base=date(2023, 7, 1),
            type_file=MATERIAL,
        )

        source_2024 = create_source_file(
            data_base=date(2024, 1, 1),
            type_file=MATERIAL,
        )

        dataframe_2023 = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        dataframe_2024 = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.85],
            ],
            columns=[
                df_code,
                df_description,
                df_unit,
                df_monetary_value,
            ],
        )

        FileXlsxProcessor(
            data_frame=dataframe_2023,
            type_file=MATERIAL,
            source_file=source_2023,
        )

        FileXlsxProcessor(
            data_frame=dataframe_2024,
            type_file=MATERIAL,
            source_file=source_2024,
        )

        item = GenericItem.objects.get(
            code="M1001"
        )

        self.assertEqual(
            item.source_files.count(),
            2,
        )

        values = MonetaryValue.objects.filter(
            generic_item=item
        ).order_by(
            "source_file__data_base"
        )

        self.assertEqual(
            values.count(),
            2,
        )

        self.assertEqual(
            Decimal(str(values[0].monetary_value)),
            Decimal("1.25"),
        )

        self.assertEqual(
            Decimal(str(values[1].monetary_value)),
            Decimal("1.85"),
        )

        self.assertEqual(
            values[0].source_file,
            source_2023,
        )

        self.assertEqual(
            values[1].source_file,
            source_2024,
        )