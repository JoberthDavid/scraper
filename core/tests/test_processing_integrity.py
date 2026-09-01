from decimal import Decimal

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

from core.usefuls.data_structure import (
    df_code,
    df_description,
    df_quantity,
    df_productive_use,
    df_unproductive_use,
    df_productive_cost,
    df_unproductive_cost,
    df_production,
    df_unit,
    df_wage,
    df_charges,
    df_monetary_value,
    df_unhealthy,
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
    PRODUTIVO,
    IMPRODUTIVO,
    AUXILIAR,
    TEMPO_FIXO,
    LEITO_NATURAL,
    REVESTIMENTO_PRIMARIO,
    PAVIMENTADO,
    FERROVIARIO,
)

from core.usefuls.processing_file import FileXlsxProcessor


class SyntheticSIProcessingIntegrityTests(TestCase):
    """
    Testes de integridade derivados da auditoria x_si_database_audit.py.

    O objetivo não é testar novamente cada preparador isoladamente.
    O objetivo é verificar o resultado final:

        DataFrame SI
            ↓
        FileXlsxProcessor
            ↓
        banco
    """

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="teste_si.xlsx",
        )

        self.dataframe = pd.DataFrame(
            [
                [
                    "1100001",
                    "Execução de concreto",
                    "m3",
                    125.5000,
                ],
                [
                    "2003979",
                    "Sarjeta trapezoidal",
                    "m",
                    4.4427,
                ],
                [
                    "1107928",
                    "Concreto fck = 20 MPa",
                    "m3",
                    379.4400,
                ],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

    def test_every_si_record_is_faithfully_persisted(self):
        """
        Cada registro do DataFrame deve resultar em:

            1 GenericItem
            1 GenericDescription
            1 relação Item -> Description
            1 MonetaryValue

        e o valor deve permanecer exatamente associado ao SourceFile.
        """

        FileXlsxProcessor(
            data_frame=self.dataframe,
            type_file=SINTETICO,
            source_file=self.source_file,
        )

        self.assertEqual(
            GenericItem.objects.filter(
                source_files=self.source_file,
            ).count(),
            len(self.dataframe),
        )

        self.assertEqual(
            MonetaryValue.objects.filter(
                source_file=self.source_file,
            ).count(),
            len(self.dataframe),
        )

        for _, row in self.dataframe.iterrows():

            code = str(row["code"])
            description = str(row["description"]).strip()
            unit = str(row["unit"]).strip()

            expected_value = Decimal(
                str(row["monetary_value"])
            )

            # --------------------------------------------------
            # GenericItem
            # --------------------------------------------------

            items = GenericItem.objects.filter(
                code=code,
                source_files=self.source_file,
            )

            self.assertEqual(
                items.count(),
                1,
                msg=f"GenericItem inválido para {code}",
            )

            item = items.get()

            # --------------------------------------------------
            # GenericDescription
            # --------------------------------------------------

            descriptions = GenericDescription.objects.filter(
                description=description,
                source_files=self.source_file,
            )

            self.assertEqual(
                descriptions.count(),
                1,
                msg=f"GenericDescription inválida para {code}",
            )

            generic_description = descriptions.get()

            # --------------------------------------------------
            # Item -> Description
            # --------------------------------------------------

            self.assertTrue(
                item.descriptions.filter(
                    pk=generic_description.pk,
                ).exists(),
                msg=(
                    f"Relação Item -> Description ausente "
                    f"para {code}"
                ),
            )

            # --------------------------------------------------
            # MonetaryValue
            # --------------------------------------------------

            values = MonetaryValue.objects.filter(
                generic_item=item,
                source_file=self.source_file,
            )

            self.assertEqual(
                values.count(),
                1,
                msg=f"MonetaryValue inválido para {code}",
            )

            monetary = values.get()

            self.assertEqual(
                Decimal(str(monetary.monetary_value)),
                expected_value,
                msg=(
                    f"Valor incorreto para {code}: "
                    f"esperado={expected_value}, "
                    f"banco={monetary.monetary_value}"
                ),
            )

            # A unidade persistida no MonetaryValue deve
            # corresponder à unidade do DataFrame.
            self.assertEqual(
                monetary.unit.unit,
                unit,
                msg=f"Unidade incorreta para {code}",
            )

    def test_processing_same_si_data_is_idempotent(self):
        """
        Processar o mesmo SI duas vezes não deve criar registros
        adicionais.
        """

        FileXlsxProcessor(
            data_frame=self.dataframe,
            type_file=SINTETICO,
            source_file=self.source_file,
        )

        first_counts = {
            "items": GenericItem.objects.count(),
            "descriptions": GenericDescription.objects.count(),
            "values": MonetaryValue.objects.count(),
        }

        FileXlsxProcessor(
            data_frame=self.dataframe,
            type_file=SINTETICO,
            source_file=self.source_file,
        )

        second_counts = {
            "items": GenericItem.objects.count(),
            "descriptions": GenericDescription.objects.count(),
            "values": MonetaryValue.objects.count(),
        }

        self.assertEqual(
            first_counts,
            second_counts,
        )

class SharedDescriptionIntegrityTests(TestCase):
    """
    Garante a regra estrutural:

        códigos diferentes podem compartilhar
        exatamente a mesma GenericDescription.
    """

    def test_different_codes_share_one_description(self):
        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="teste_si.xlsx",
        )

        dataframe = pd.DataFrame(
            [
                [
                    "1100001",
                    "Cimento Portland",
                    "kg",
                    10.25,
                ],
                [
                    "1100002",
                    "Cimento Portland",
                    "kg",
                    11.75,
                ],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=SINTETICO,
            source_file=source_file,
        )

        self.assertEqual(
            GenericItem.objects.count(),
            2,
        )

        self.assertEqual(
            GenericDescription.objects.count(),
            1,
        )

        description = GenericDescription.objects.get(
            description="Cimento Portland",
        )

        items = GenericItem.objects.filter(
            source_files=source_file,
        )

        self.assertEqual(
            items.count(),
            2,
        )

        for item in items:
            self.assertIn(
                description,
                item.descriptions.all(),
            )

        self.assertEqual(
            description.generic_items.count(),
            2,
        )

        values = MonetaryValue.objects.filter(
            source_file=source_file,
        ).order_by(
            "generic_item__code"
        )

        self.assertEqual(
            values.count(),
            2,
        )

        self.assertEqual(
            Decimal(str(values[0].monetary_value)),
            Decimal("10.25"),
        )

        self.assertEqual(
            Decimal(str(values[1].monetary_value)),
            Decimal("11.75"),
        )

class EquipmentProcessingIntegrityTests(TestCase):
    """
    Testes de integridade derivados da auditoria de equipamentos.

    O objetivo é verificar o pipeline:

        DataFrame EQ
            ↓
        FileXlsxProcessor
            ↓
        GenericItem
        GenericDescription
        EquipmentItem
        MonetaryValue PRODUTIVO
        MonetaryValue IMPRODUTIVO
    """

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=EQUIPAMENTO,
            uf=GOIAS,
            source_file="teste_eq.xlsx",
        )

        self.dataframe = pd.DataFrame(
            [
                [
                    "E1001",
                    "Escavadeira",
                    100000.0,
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
                "code",
                "description",
                "purchase_value",
                "deprecation",
                "equity_opportunity",
                "insurance_and_taxes",
                "maintenance",
                "operation",
                "labor",
                "productive_cost",
                "unproductive_cost",
            ],
        )

        self.dataframe["unit"] = "h"

    def test_analytical_processing_creates_equipment_item(self):
        """
        EquipmentItem é criado a partir do arquivo ANALÍTICO.

        Fluxo:

            composição
                ↓
            linha de equipamento [EA]####
                ↓
            AllocationPreparer
                ↓
            EquipmentItem
        """

        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=ANALITICO,
            uf=GOIAS,
            source_file="teste_an.xlsx",
        )

        synthetic_source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base=source_file.data_base,
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="teste_si.xlsx",
        )

        unit_m3 = Unit.objects.create(
            unit="m3",
        )

        unit_h = Unit.objects.create(
            unit="h",
        )

        composition_item = GenericItem.objects.create(
            code="1100001",
        )

        composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        equipment_item = GenericItem.objects.create(
            code="E1001",
        )

        equipment_description = GenericDescription.objects.create(
            description="Escavadeira",
            group=EQUIPAMENTO,
        )

        composition_item.source_files.add(
            source_file,
            synthetic_source_file,
        )

        composition_description.source_files.add(
            source_file,
            synthetic_source_file,
        )

        equipment_item.source_files.add(
            source_file,
        )

        equipment_description.source_files.add(
            source_file,
        )

        composition_description.generic_items.add(
            composition_item,
        )

        equipment_description.generic_items.add(
            equipment_item,
        )


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
                    0.10000,
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
                    24.63000,
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
                [
                    "E1001",
                    "Escavadeira",
                    1.50000,
                    2.00000,
                    1.00000,
                    42.19300,
                    28.02380,
                    0,
                    "h",
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

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        equipment = EquipmentItem.objects.get(
            composition=composition,
            generic_item=equipment_item,
        )

        self.assertEqual(
            equipment.input_quantity,
            Decimal("1.50000"),
        )

        self.assertEqual(
            equipment.input_use,
            Decimal("2.00000"),
        )

        self.assertEqual(
            equipment.unit,
            unit_h,
        )

        self.assertEqual(
            equipment.input_group,
            EQUIPAMENTO,
        )

        self.assertIn(
            source_file,
            equipment.source_files.all(),
        )

    def test_equipment_productive_and_unproductive_values_match_xlsx(self):
        """
        Cada equipamento deve possuir:

            1 MonetaryValue PRODUTIVO
            1 MonetaryValue IMPRODUTIVO

        e seus valores devem corresponder exatamente ao XLSX.
        """

        FileXlsxProcessor(
            data_frame=self.dataframe,
            type_file=EQUIPAMENTO,
            source_file=self.source_file,
        )

        item = GenericItem.objects.get(
            code="E1001",
        )

        values = MonetaryValue.objects.filter(
            generic_item=item,
            source_file=self.source_file,
        )

        self.assertEqual(
            values.count(),
            2,
        )

        productive = values.get(
            classification=PRODUTIVO,
        )

        unproductive = values.get(
            classification=IMPRODUTIVO,
        )

        self.assertEqual(
            productive.group,
            EQUIPAMENTO,
        )

        self.assertEqual(
            productive.type_system,
            self.source_file.type_system,
        )

        self.assertEqual(
            unproductive.group,
            EQUIPAMENTO,
        )

        self.assertEqual(
            unproductive.type_system,
            self.source_file.type_system,
        )

        self.assertEqual(
            productive.unit.unit,
            "h",
        )

        self.assertEqual(
            unproductive.unit.unit,
            "h",
        )

        self.assertEqual(
            Decimal(str(productive.monetary_value)),
            Decimal("100.00"),
        )

        self.assertEqual(
            Decimal(str(unproductive.monetary_value)),
            Decimal("80.00"),
        )


class WorkmanProcessingIntegrityTests(TestCase):
    """
    Testes de integridade para MÃO DE OBRA.

    Separamos os dois fluxos:

        MO
        ↓
        GenericItem
        GenericDescription
        MonetaryValue

    e:

        AN
        ↓
        Composition
        ↓
        AllocationPreparer
        ↓
        WorkmanItem
    """

    def test_workman_synthetic_data_is_faithfully_persisted(self):
        """
        O arquivo MO deve preservar código, descrição, unidade
        e valor monetário no SourceFile correto.
        """

        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=MAODEOBRA,
            uf=GOIAS,
            source_file="teste_mo.xlsx",
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
            code="P9821",
        )

        description = GenericDescription.objects.get(
            description="Pedreiro",
        )

        self.assertIn(
            source_file,
            item.source_files.all(),
        )

        self.assertIn(
            source_file,
            description.source_files.all(),
        )

        self.assertIn(
            description,
            item.descriptions.all(),
        )

        monetary_value = MonetaryValue.objects.get(
            generic_item=item,
            source_file=source_file,
        )

        self.assertEqual(
            monetary_value.classification,
            CUSTO,
        )

        self.assertEqual(
            monetary_value.group,
            MAODEOBRA,
        )

        self.assertEqual(
            monetary_value.unit.unit,
            "h",
        )

        self.assertEqual(
            Decimal(str(monetary_value.monetary_value)),
            Decimal("35.0"),
        )

    def test_analytical_processing_creates_workman_item(self):
        """
        Uma linha P#### no ANALÍTICO deve gerar WorkmanItem
        associado à composição correta.
        """

        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=ANALITICO,
            uf=GOIAS,
            source_file="teste_an.xlsx",
        )

        synthetic_source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base=source_file.data_base,
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="teste_si.xlsx",
        )

        unit_m3 = Unit.objects.create(
            unit="m3",
        )

        unit_h = Unit.objects.create(
            unit="h",
        )

        composition_item = GenericItem.objects.create(
            code="1100001",
        )

        composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        workman_item = GenericItem.objects.create(
            code="P9821",
        )

        workman_description = GenericDescription.objects.create(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        composition_item.source_files.add(
            source_file,
            synthetic_source_file,
        )

        composition_description.source_files.add(
            source_file,
            synthetic_source_file,
        )

        workman_item.source_files.add(
            source_file,
        )

        workman_description.source_files.add(
            source_file,
        )

        composition_description.generic_items.add(
            composition_item,
        )

        workman_description.generic_items.add(
            workman_item,
        )

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
                    0.10000,
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
                    24.63000,
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
                [
                    "P9821",
                    "Pedreiro",
                    2.50000,
                    "h",
                    None,
                    27.54680,
                    None,
                    0,
                    "h",
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

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        workman = WorkmanItem.objects.get(
            composition=composition,
            generic_item=workman_item,
        )

        self.assertEqual(
            workman.generic_description,
            workman_description,
        )

        self.assertEqual(
            workman.input_quantity,
            Decimal("2.50000"),
        )

        self.assertEqual(
            workman.unit,
            unit_h,
        )

        self.assertEqual(
            workman.input_group,
            MAODEOBRA,
        )

        self.assertIn(
            source_file,
            workman.source_files.all(),
        )


class MaterialProcessingIntegrityTests(TestCase):

    def test_material_synthetic_data_is_faithfully_persisted(self):
        """
        O arquivo MA deve preservar código, descrição, unidade
        e valor monetário no SourceFile correto.
        """

        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=MATERIAL,
            uf=GOIAS,
            source_file="teste_ma.xlsx",
        )

        dataframe = pd.DataFrame(
            [
                [
                    "M1001",
                    "Cimento",
                    "kg",
                    1.25,
                ],
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

        item = GenericItem.objects.get(
            code="M1001",
        )

        description = GenericDescription.objects.get(
            description="Cimento",
        )

        self.assertIn(
            source_file,
            item.source_files.all(),
        )

        self.assertIn(
            source_file,
            description.source_files.all(),
        )

        self.assertIn(
            description,
            item.descriptions.all(),
        )

        monetary_value = MonetaryValue.objects.get(
            generic_item=item,
            source_file=source_file,
        )

        self.assertEqual(
            monetary_value.classification,
            CUSTO,
        )

        self.assertEqual(
            monetary_value.group,
            MATERIAL,
        )

        self.assertEqual(
            monetary_value.unit.unit,
            "kg",
        )

        self.assertEqual(
            Decimal(str(monetary_value.monetary_value)),
            Decimal("1.25"),
        )

    def test_analytical_processing_creates_material_item(self):
        """
        Uma linha M#### no ANALÍTICO deve gerar MaterialItem
        associado à composição correta.
        """

        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=ANALITICO,
            uf=GOIAS,
            source_file="teste_an.xlsx",
        )

        synthetic_source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base=source_file.data_base,
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="teste_si.xlsx",
        )

        unit_m3 = Unit.objects.create(
            unit="m3",
        )

        unit_kg = Unit.objects.create(
            unit="kg",
        )

        composition_item = GenericItem.objects.create(
            code="1100001",
        )

        composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        material_item = GenericItem.objects.create(
            code="M1001",
        )

        material_description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        composition_item.source_files.add(
            source_file,
            synthetic_source_file,
        )

        composition_description.source_files.add(
            source_file,
            synthetic_source_file,
        )

        material_item.source_files.add(
            source_file,
        )

        material_description.source_files.add(
            source_file,
        )

        composition_description.generic_items.add(
            composition_item,
        )

        material_description.generic_items.add(
            material_item,
        )

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
                    0.10000,
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
                    24.63000,
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
                [
                    "M1001",
                    "Cimento",
                    2.50000,
                    "kg",
                    None,
                    80.00000,
                    None,
                    0,
                    "kg",
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

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        material = MaterialItem.objects.get(
            composition=composition,
            generic_item=material_item,
        )

        self.assertEqual(
            material.generic_description,
            material_description,
        )

        self.assertEqual(
            material.input_quantity,
            Decimal("2.50000"),
        )

        self.assertEqual(
            material.unit,
            unit_kg,
        )

        self.assertEqual(
            material.input_group,
            MATERIAL,
        )

        self.assertIn(
            source_file,
            material.source_files.all(),
        )


class AuxiliaryActivityProcessingIntegrityTests(TestCase):
    """
    Teste de integridade para atividades auxiliares.

    A atividade auxiliar nasce do arquivo ANALÍTICO.

        AN
        ↓
        composição
        ↓
        código numérico de 7 dígitos
        ↓
        AuxiliaryActivityItem
    """

    def test_analytical_processing_creates_auxiliary_activity_item(self):
        """
        Uma linha de atividade auxiliar no ANALÍTICO deve gerar
        AuxiliaryActivityItem associado à composição correta.
        """

        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=ANALITICO,
            uf=GOIAS,
            source_file="teste_an.xlsx",
        )

        synthetic_source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base=source_file.data_base,
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="teste_si.xlsx",
        )

        unit_m3 = Unit.objects.create(
            unit="m3",
        )

        composition_item = GenericItem.objects.create(
            code="1100001",
        )

        composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        activity_item = GenericItem.objects.create(
            code="1107928",
        )

        activity_description = GenericDescription.objects.create(
            description="Concreto fck = 20 MPa",
            group=MATERIAL,
        )

        composition_item.source_files.add(
            source_file,
            synthetic_source_file,
        )

        composition_description.source_files.add(
            source_file,
            synthetic_source_file,
        )

        activity_item.source_files.add(
            source_file,
        )

        activity_description.source_files.add(
            source_file,
        )

        composition_description.generic_items.add(
            composition_item,
        )

        activity_description.generic_items.add(
            activity_item,
        )

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
                    0.10000,
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
                    24.63000,
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
                [
                    "1107928",
                    "Concreto fck = 20 MPa",
                    0.13900,
                    "m3",
                    None,
                    None,
                    None,
                    0,
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

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        activity = AuxiliaryActivityItem.objects.get(
            composition=composition,
            generic_item=activity_item,
        )

        self.assertEqual(
            activity.generic_description,
            activity_description,
        )

        self.assertEqual(
            activity.input_quantity,
            Decimal("0.13900"),
        )

        self.assertEqual(
            activity.unit.unit,
            "m3",
        )

        self.assertEqual(
            activity.input_group,
            AUXILIAR,
        )

        self.assertIn(
            source_file,
            activity.source_files.all(),
        )

class TransportProcessingIntegrityTests(TestCase):
    """
    Testes das cinco classificações de transporte reconhecidas pelo
    AllocationPreparer:

        TEMPO_FIXO
        LEITO_NATURAL
        REVESTIMENTO_PRIMARIO
        PAVIMENTADO
        FERROVIARIO
    """

    def _create_context(self):
        source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base="2023-01-01",
            type_system=ONERADO,
            type_file=ANALITICO,
            uf=GOIAS,
            source_file="teste_an.xlsx",
        )

        synthetic_source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base=source_file.data_base,
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="teste_si.xlsx",
        )

        unit_m3 = Unit.objects.create(
            unit="m3",
        )

        unit_t = Unit.objects.create(
            unit="t",
        )

        unit_tkm = Unit.objects.create(
            unit="tkm",
        )

        composition_item = GenericItem.objects.create(
            code="1100001",
        )

        composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        composition_item.source_files.add(
            source_file,
            synthetic_source_file,
        )

        composition_description.source_files.add(
            source_file,
            synthetic_source_file,
        )

        composition_description.generic_items.add(
            composition_item,
        )

        return (
            source_file,
            composition_item,
            unit_m3,
            unit_t,
            unit_tkm,
        )

    def _create_transport_entity(
        self,
        source_file,
        code,
        description,
    ):
        item = GenericItem.objects.create(
            code=code,
        )

        generic_description = GenericDescription.objects.create(
            description=description,
            group=COMPOSICAO,
        )

        item.source_files.add(
            source_file,
        )

        generic_description.source_files.add(
            source_file,
        )

        generic_description.generic_items.add(
            item,
        )

        return item, generic_description

    def _create_proprietary_item(
        self,
        source_file,
        code="1107928",
    ):
        proprietary = GenericItem.objects.create(
            code=code,
        )

        proprietary_description = GenericDescription.objects.create(
            description="Insumo proprietário",
            group=MATERIAL,
        )

        proprietary.source_files.add(
            source_file,
        )

        proprietary_description.source_files.add(
            source_file,
        )

        proprietary_description.generic_items.add(
            proprietary,
        )

        return proprietary

    def _base_dataframe(self, transport_row):
        return pd.DataFrame(
            [
                [
                    "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS - SICRO",
                    "",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0.10000,
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
                    24.63000,
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
                transport_row,
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

    def test_analytical_processing_creates_fixed_time_transport(self):
        """
        TEMPO_FIXO:

            código do transporte = df_quantity
            quantidade          = df_productive_use
            unidade             = df_unproductive_use
            proprietário        = df_code
        """

        source_file, composition_item, unit_m3, unit_t, unit_tkm = (
            self._create_context()
        )

        transport_item, transport_description = (
            self._create_transport_entity(
                source_file,
                "5914569",
                "Carga, manobra e descarga",
            )
        )

        proprietary = self._create_proprietary_item(
            source_file,
            "1107928",
        )

        dataframe = self._base_dataframe(
            [
                "1107928",              # proprietário
                "Equipamento proprietário",
                "5914569",              # código do transporte
                Decimal("0.33360"),     # quantidade
                "t",                    # unidade
                0,
                0,
                0,
                "tkm",
            ]
        )

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        transport = TransportItem.objects.get(
            composition=composition,
            generic_item=transport_item,
        )

        self.assertEqual(
            transport.generic_description,
            transport_description,
        )

        self.assertEqual(
            transport.input_group,
            TEMPO_FIXO,
        )

        self.assertEqual(
            transport.input_quantity,
            Decimal("0.33360"),
        )

        self.assertEqual(
            transport.unit,
            unit_t,
        )

        self.assertEqual(
            transport.proprietary_item,
            proprietary,
        )

        self.assertIn(
            source_file,
            transport.source_files.all(),
        )

    def test_analytical_processing_creates_three_road_transport_items(self):
        """
        Uma linha que satisfaz a regra de transporte rodoviário deve gerar:

            LEITO_NATURAL
            REVESTIMENTO_PRIMARIO
            PAVIMENTADO

        Os três códigos vêm de:

            df_unproductive_use
            df_productive_cost
            df_unproductive_cost
        """

        source_file, composition_item, unit_m3, unit_t, unit_tkm = (
            self._create_context()
        )

        natural_item, natural_description = (
            self._create_transport_entity(
                source_file,
                "5914569",
                "Transporte em leito natural",
            )
        )

        primary_item, primary_description = (
            self._create_transport_entity(
                source_file,
                "5914570",
                "Transporte em revestimento primário",
            )
        )

        paved_item, paved_description = (
            self._create_transport_entity(
                source_file,
                "5914571",
                "Transporte em pavimentado",
            )
        )

        proprietary = self._create_proprietary_item(
            source_file,
            "1107928",
        )

        dataframe = self._base_dataframe(
            [
                "1107928",       # proprietário
                "Material proprietário",
                Decimal("0.75000"),
                "tkm",           # unidade
                "5914569",       # LN
                "5914570",       # RP
                "5914571",       # PV
                0,
                "tkm",
            ]
        )

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        natural = TransportItem.objects.get(
            composition=composition,
            generic_item=natural_item,
        )

        primary = TransportItem.objects.get(
            composition=composition,
            generic_item=primary_item,
        )

        paved = TransportItem.objects.get(
            composition=composition,
            generic_item=paved_item,
        )

        for transport in (
            natural,
            primary,
            paved,
        ):
            self.assertEqual(
                transport.input_quantity,
                Decimal("0.75000"),
            )

            self.assertEqual(
                transport.unit,
                unit_tkm,
            )

            self.assertEqual(
                transport.proprietary_item,
                proprietary,
            )

            self.assertIn(
                source_file,
                transport.source_files.all(),
            )

        self.assertEqual(
            natural.input_group,
            LEITO_NATURAL,
        )

        self.assertEqual(
            natural.generic_description,
            natural_description,
        )

        self.assertEqual(
            primary.input_group,
            REVESTIMENTO_PRIMARIO,
        )

        self.assertEqual(
            primary.generic_description,
            primary_description,
        )

        self.assertEqual(
            paved.input_group,
            PAVIMENTADO,
        )

        self.assertEqual(
            paved.generic_description,
            paved_description,
        )

    def test_analytical_processing_creates_railway_transport_item(self):
        """
        FERROVIARIO:

            código do transporte = df_production
            quantidade          = df_quantity
            unidade             = df_productive_use
            proprietário        = df_code
        """

        source_file, composition_item, unit_m3, unit_t, unit_tkm = (
            self._create_context()
        )

        transport_item, transport_description = (
            self._create_transport_entity(
                source_file,
                "5914569",
                "Transporte ferroviário",
            )
        )

        proprietary = self._create_proprietary_item(
            source_file,
            "1107928",
        )

        dataframe = self._base_dataframe(
            [
                "1107928",
                "Material proprietário",
                Decimal("1.25000"),
                "tkm",
                None,
                None,
                None,
                "5914569",
                "tkm",
            ]
        )

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        transport = TransportItem.objects.get(
            composition=composition,
            generic_item=transport_item,
        )

        self.assertEqual(
            transport.generic_description,
            transport_description,
        )

        self.assertEqual(
            transport.input_group,
            FERROVIARIO,
        )

        self.assertEqual(
            transport.input_quantity,
            Decimal("1.25000"),
        )

        self.assertEqual(
            transport.unit,
            unit_tkm,
        )

        self.assertEqual(
            transport.proprietary_item,
            proprietary,
        )

        self.assertIn(
            source_file,
            transport.source_files.all(),
        )

class NumericPrecisionProcessingIntegrityTests(TestCase):
    """
    Testes de precisão de acordo com o contrato atual dos Models.

    MonetaryValue:
        decimal_places=4

    InputQuantity:
        decimal_places=5
    """

    def _create_source_file(
        self,
        *,
        data_base,
        source_file_name,
    ):
        return SourceFile.objects.create(
            methodology=SICRO,
            data_base=data_base,
            type_system=ONERADO,
            type_file=MATERIAL,
            uf=GOIAS,
            source_file=source_file_name,
        )

    def test_monetary_value_is_rounded_to_four_decimal_places(self):
        """
        MonetaryValue possui decimal_places=4.

        Portanto:

            123.45678 → 123.4568
        """

        source_file = self._create_source_file(
            data_base="2023-01-01",
            source_file_name="precision_2023.xlsx",
        )

        dataframe = pd.DataFrame(
            [
                [
                    "M1001",
                    "Material de precisão",
                    "kg",
                    123.45678,
                ],
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

        item = GenericItem.objects.get(
            code="M1001",
        )

        monetary_value = MonetaryValue.objects.get(
            generic_item=item,
            source_file=source_file,
        )

        self.assertEqual(
            Decimal(str(monetary_value.monetary_value)),
            Decimal("123.4568"),
        )

    def test_material_quantity_preserves_five_decimal_places(self):
        """
        MaterialItem possui input_quantity com cinco casas decimais.

        O valor deve ser preservado integralmente:
        
            1.23456 → 1.23456
        """

        source_file = self._create_source_file(
            data_base="2023-01-01",
            source_file_name="precision_an_2023.xlsx",
        )

        synthetic_source_file = SourceFile.objects.create(
            methodology=SICRO,
            data_base=source_file.data_base,
            type_system=ONERADO,
            type_file=SINTETICO,
            uf=GOIAS,
            source_file="precision_si_2023.xlsx",
        )

        Unit.objects.create(
            unit="m3",
        )

        Unit.objects.create(
            unit="kg",
        )

        composition_item = GenericItem.objects.create(
            code="1100001",
        )

        composition_description = GenericDescription.objects.create(
            description="Composição de precisão",
            group=COMPOSICAO,
        )

        material_item = GenericItem.objects.create(
            code="M1001",
        )

        material_description = GenericDescription.objects.create(
            description="Material de precisão",
            group=MATERIAL,
        )

        composition_item.source_files.add(
            source_file,
            synthetic_source_file,
        )

        composition_description.source_files.add(
            source_file,
            synthetic_source_file,
        )

        material_item.source_files.add(
            source_file,
        )

        material_description.source_files.add(
            source_file,
        )

        composition_description.generic_items.add(
            composition_item,
        )

        material_description.generic_items.add(
            material_item,
        )

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
                    0.12345,
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
                    24.63001,
                    "m3",
                ],
                [
                    "1100001",
                    "Composição de precisão",
                    1,
                    0,
                    0,
                    0,
                    0,
                    "Valores em reais (R$)",
                    "m3",
                ],
                [
                    "M1001",
                    "Material de precisão",
                    1.23456,
                    "kg",
                    None,
                    None,
                    None,
                    0,
                    "kg",
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

        FileXlsxProcessor(
            data_frame=dataframe,
            type_file=ANALITICO,
            source_file=source_file,
        )

        composition = Composition.objects.get(
            generic_item=composition_item,
        )

        material = MaterialItem.objects.get(
            composition=composition,
            generic_item=material_item,
        )

        self.assertEqual(
            material.input_quantity,
            Decimal("1.23456"),
        )

    def test_historical_values_remain_distinct_after_model_precision(self):
        """
        O mesmo código em duas data-bases deve continuar possuindo
        dois valores distintos depois da precisão de quatro casas
        do MonetaryValue.

            2023 → 1.23451 → 1.2345
            2024 → 1.23459 → 1.2346
        """

        source_2023 = self._create_source_file(
            data_base="2023-01-01",
            source_file_name="precision_2023.xlsx",
        )

        source_2024 = self._create_source_file(
            data_base="2024-01-01",
            source_file_name="precision_2024.xlsx",
        )

        dataframe_2023 = pd.DataFrame(
            [
                [
                    "M1001",
                    "Material histórico",
                    "kg",
                    1.23451,
                ],
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
                [
                    "M1001",
                    "Material histórico",
                    "kg",
                    1.23459,
                ],
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
            code="M1001",
        )

        values = MonetaryValue.objects.filter(
            generic_item=item,
        ).order_by(
            "source_file__data_base",
        )

        self.assertEqual(
            values.count(),
            2,
        )

        self.assertEqual(
            Decimal(str(values[0].monetary_value)),
            Decimal("1.2345"),
        )

        self.assertEqual(
            Decimal(str(values[1].monetary_value)),
            Decimal("1.2346"),
        )

        self.assertNotEqual(
            values[0].monetary_value,
            values[1].monetary_value,
        )