from decimal import Decimal
from datetime import date

import pandas as pd

from django.test import TestCase

from core.models import (
    SourceFile,
    Unit,
    GenericItem,
    GenericDescription,
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
    EQUIPAMENTO,
    MAODEOBRA,
    MATERIAL,
    COMPOSICAO,
    AUXILIAR,
    TEMPO_FIXO,
    LEITO_NATURAL,
    REVESTIMENTO_PRIMARIO,
    PAVIMENTADO,
)

from core.usefuls.data_structure import (
    CompositionPreparer,
    InputEquipmentPreparer,
    InputWorkmanPreparer,
    InputMaterialPreparer,
    InputAuxiliaryActivityPreparer,
    InputTransportPreparer,
)


def create_source_file(type_file=ANALITICO):
    return SourceFile.objects.create(
        methodology=SICRO,
        data_base="2023-07-01",
        source_file="teste.xlsx",
        uf=GOIAS,
        type_system=ONERADO,
        type_file=type_file,
    )


class CompositionPreparerTests(TestCase):

    def setUp(self):
        self.composition_item = GenericItem.objects.create(
            code="2003979",
        )

        self.description = GenericDescription.objects.create(
            description="Sarjeta trapezoidal",
            group=COMPOSICAO,
        )

        self.unit = Unit.objects.create(
            unit="m",
        )

    def test_initial_state_is_empty(self):
        preparer = CompositionPreparer()

        self.assertEqual(preparer.code_list, [])
        self.assertEqual(preparer.description_list, [])
        self.assertEqual(preparer.production_list, [])
        self.assertEqual(preparer.unit_list, [])
        self.assertEqual(preparer.fic_list, [])
        self.assertEqual(preparer.group_list, [])
        self.assertEqual(preparer.bulk_create_list, [])

    def test_append_methods_store_values_in_order(self):
        preparer = CompositionPreparer()

        preparer.append_code("2003979")
        preparer.append_description("Sarjeta trapezoidal")
        preparer.append_production(24.63)
        preparer.append_unit("m")
        preparer.append_fic(0.0)
        preparer.append_group("20")

        self.assertEqual(
            preparer.code_list,
            ["2003979"],
        )

        self.assertEqual(
            preparer.description_list,
            ["Sarjeta trapezoidal"],
        )

        self.assertEqual(
            preparer.production_list,
            [24.63],
        )

        self.assertEqual(
            preparer.unit_list,
            ["m"],
        )

        self.assertEqual(
            preparer.fic_list,
            [0.0],
        )

        self.assertEqual(
            preparer.group_list,
            ["20"],
        )

    def test_get_bulk_create_list_creates_composition_instances(self):
        preparer = CompositionPreparer()

        preparer.append_code(self.composition_item)
        preparer.append_description(self.description)
        preparer.append_production(Decimal("24.63000"))
        preparer.append_unit(self.unit)
        preparer.append_fic(Decimal("0.00000"))
        preparer.append_group("20")

        result = preparer.get_bulk_create_list()

        self.assertEqual(len(result), 1)

        composition = result[0]

        self.assertIsInstance(
            composition,
            Composition,
        )

        self.assertEqual(
            composition.generic_item,
            self.composition_item,
        )

        self.assertEqual(
            composition.generic_description,
            self.description,
        )

        self.assertEqual(
            composition.unit,
            self.unit,
        )

        self.assertEqual(
            composition.production,
            Decimal("24.63000"),
        )

        self.assertEqual(
            composition.fic,
            Decimal("0.00000"),
        )

        self.assertEqual(
            composition.composition_group,
            "20",
        )

    def test_get_bulk_create_list_preserves_multiple_compositions(self):
        item_2 = GenericItem.objects.create(
            code="2003980",
        )

        description_2 = GenericDescription.objects.create(
            description="Outra composição",
            group=COMPOSICAO,
        )

        preparer = CompositionPreparer()

        preparer.append_code(self.composition_item)
        preparer.append_description(self.description)
        preparer.append_production(Decimal("24.63000"))
        preparer.append_unit(self.unit)
        preparer.append_fic(Decimal("0.00000"))
        preparer.append_group("20")

        preparer.append_code(item_2)
        preparer.append_description(description_2)
        preparer.append_production(Decimal("10.50000"))
        preparer.append_unit(self.unit)
        preparer.append_fic(Decimal("0.10000"))
        preparer.append_group("20")

        result = preparer.get_bulk_create_list()

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0].generic_item,
            self.composition_item,
        )

        self.assertEqual(
            result[1].generic_item,
            item_2,
        )


class InputEquipmentPreparerTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file()

        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="2003979",
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m",
            ),
            production=Decimal("24.63000"),
            fic=Decimal("0.00000"),
            composition_group="20",
        )

        self.item = GenericItem.objects.create(
            code="E9102",
        )

        self.description = GenericDescription.objects.create(
            description="Extrusora",
            group=EQUIPAMENTO,
        )

        self.unit = Unit.objects.create(
            unit="h",
        )

    def test_append_input_preserves_equipment_data(self):
        preparer = InputEquipmentPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.item,
            description=self.description,
            group=EQUIPAMENTO,
            quantity=Decimal("1.00000"),
            use=Decimal("1.00000"),
            unit=self.unit,
        )

        self.assertEqual(
            preparer.composition_list,
            [self.composition],
        )

        self.assertEqual(
            preparer.input_code_list,
            [self.item],
        )

        self.assertEqual(
            preparer.input_description_list,
            [self.description],
        )

        self.assertEqual(
            preparer.input_group_list,
            [EQUIPAMENTO],
        )

        self.assertEqual(
            preparer.input_quantity_list,
            [Decimal("1.00000")],
        )

        self.assertEqual(
            preparer.input_productive_use_list,
            [Decimal("1.00000")],
        )

        self.assertEqual(
            preparer.input_unit_list,
            [self.unit],
        )

    def test_get_bulk_create_list_returns_equipment_items(self):
        preparer = InputEquipmentPreparer()

        preparer.append_input(
            self.composition,
            self.item,
            self.description,
            EQUIPAMENTO,
            Decimal("1.00000"),
            Decimal("1.00000"),
            self.unit,
        )

        result = preparer.get_bulk_create_list()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], EquipmentItem)

        self.assertEqual(
            result[0].composition,
            self.composition,
        )

        self.assertEqual(
            result[0].generic_item,
            self.item,
        )

        self.assertEqual(
            result[0].generic_description,
            self.description,
        )

        self.assertEqual(
            result[0].input_quantity,
            Decimal("1.00000"),
        )

        self.assertEqual(
            result[0].input_use,
            Decimal("1.00000"),
        )

        self.assertEqual(
            result[0].unit,
            self.unit,
        )


class InputGenericPreparerInheritanceTests(TestCase):

    def test_workman_preparer_inherits_generic_preparer(self):
        preparer = InputWorkmanPreparer()

        self.assertIsInstance(
            preparer,
            InputWorkmanPreparer,
        )

        self.assertTrue(
            hasattr(preparer, "composition_list")
        )

        self.assertTrue(
            hasattr(preparer, "input_code_list")
        )

        self.assertTrue(
            hasattr(preparer, "input_description_list")
        )

        self.assertTrue(
            hasattr(preparer, "input_group_list")
        )

        self.assertTrue(
            hasattr(preparer, "input_quantity_list")
        )

        self.assertTrue(
            hasattr(preparer, "input_unit_list")
        )

    def test_material_preparer_inherits_generic_preparer(self):
        preparer = InputMaterialPreparer()

        self.assertTrue(
            hasattr(preparer, "composition_list")
        )

        self.assertTrue(
            hasattr(preparer, "input_code_list")
        )

    def test_auxiliary_activity_preparer_inherits_generic_preparer(self):
        preparer = InputAuxiliaryActivityPreparer()

        self.assertTrue(
            hasattr(preparer, "composition_list")
        )

        self.assertTrue(
            hasattr(preparer, "input_code_list")
        )


class InputWorkmanPreparerTests(TestCase):

    def setUp(self):
        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="2003979",
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m",
            ),
            production=Decimal("24.63000"),
            fic=Decimal("0.00000"),
            composition_group="20",
        )

        self.item = GenericItem.objects.create(
            code="P9821",
        )

        self.description = GenericDescription.objects.create(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        self.unit = Unit.objects.create(
            unit="h",
        )

    def test_get_bulk_create_list_creates_workman_item(self):
        preparer = InputWorkmanPreparer()

        preparer.append_input(
            self.composition,
            self.item,
            self.description,
            MAODEOBRA,
            Decimal("1.00000"),
            self.unit,
        )

        result = preparer.get_bulk_create_list()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], WorkmanItem)

        self.assertEqual(
            result[0].input_quantity,
            Decimal("1.00000"),
        )

        self.assertEqual(
            result[0].unit,
            self.unit,
        )


class InputMaterialPreparerTests(TestCase):

    def setUp(self):
        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="2003979",
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m",
            ),
            production=Decimal("24.63000"),
            fic=Decimal("0.00000"),
            composition_group="20",
        )

        self.item = GenericItem.objects.create(
            code="M1001",
        )

        self.description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        self.unit = Unit.objects.create(
            unit="kg",
        )

    def test_get_bulk_create_list_creates_material_item(self):
        preparer = InputMaterialPreparer()

        preparer.append_input(
            self.composition,
            self.item,
            self.description,
            MATERIAL,
            Decimal("2.50000"),
            self.unit,
        )

        result = preparer.get_bulk_create_list()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], MaterialItem)

        self.assertEqual(
            result[0].generic_item,
            self.item,
        )

        self.assertEqual(
            result[0].input_quantity,
            Decimal("2.50000"),
        )


class InputAuxiliaryActivityPreparerTests(TestCase):

    def setUp(self):
        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="2003979",
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m",
            ),
            production=Decimal("24.63000"),
            fic=Decimal("0.00000"),
            composition_group="20",
        )

        self.item = GenericItem.objects.create(
            code="1107928",
        )

        self.description = GenericDescription.objects.create(
            description="Concreto",
            group=COMPOSICAO,
        )

        self.unit = Unit.objects.create(
            unit="m3",
        )

    def test_get_bulk_create_list_creates_auxiliary_activity_item(self):
        preparer = InputAuxiliaryActivityPreparer()

        preparer.append_input(
            self.composition,
            self.item,
            self.description,
            AUXILIAR,
            Decimal("0.13900"),
            self.unit,
        )

        result = preparer.get_bulk_create_list()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(
            result[0],
            AuxiliaryActivityItem,
        )

        self.assertEqual(
            result[0].input_quantity,
            Decimal("0.13900"),
        )

        self.assertEqual(
            result[0].input_group,
            AUXILIAR,
        )


class InputTransportPreparerTests(TestCase):

    def setUp(self):
        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="2003979",
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m",
            ),
            production=Decimal("24.63000"),
            fic=Decimal("0.00000"),
            composition_group="20",
        )

        self.transport_item = GenericItem.objects.create(
            code="5919534",
        )

        self.transport_description = GenericDescription.objects.create(
            description="Carga, manobra e descarga",
            group=COMPOSICAO,
        )

        self.unit = Unit.objects.create(
            unit="t",
        )

        self.proprietary = GenericItem.objects.create(
            code="1107928",
        )

    def test_append_input_preserves_proprietary_item(self):
        preparer = InputTransportPreparer()

        preparer.append_input(
            self.composition,
            self.transport_item,
            self.transport_description,
            TEMPO_FIXO,
            Decimal("0.33360"),
            self.unit,
            self.proprietary,
        )

        self.assertEqual(
            preparer.input_proprietary_list,
            [self.proprietary],
        )

    def test_get_bulk_create_list_creates_transport_item(self):
        preparer = InputTransportPreparer()

        preparer.append_input(
            self.composition,
            self.transport_item,
            self.transport_description,
            LEITO_NATURAL,
            Decimal("0.33360"),
            self.unit,
            self.proprietary,
        )

        result = preparer.get_bulk_create_list()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(
            result[0],
            TransportItem,
        )

        self.assertEqual(
            result[0].generic_item,
            self.transport_item,
        )

        self.assertEqual(
            result[0].input_quantity,
            Decimal("0.33360"),
        )

        self.assertEqual(
            result[0].proprietary_item,
            self.proprietary,
        )

        self.assertEqual(
            result[0].input_group,
            LEITO_NATURAL,
        )

# ============================================================================
# SEGUNDO BLOCO — PERSISTÊNCIA E RELACIONAMENTOS
# ============================================================================

class InputEquipmentPersistenceTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file(
            type_file=EQUIPAMENTO,
        )

        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="1000001"
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição teste",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m"
            ),
            fic=Decimal("0.00000"),
            production=Decimal("10.00000"),
            composition_group="20",
        )

        # IMPORTANTE:
        # create_instances() procura os itens através da Composition
        # relacionada ao SourceFile.
        self.composition.source_files.add(
            self.source_file
        )

        self.item = GenericItem.objects.create(
            code="E1001",
        )

        self.description = GenericDescription.objects.create(
            description="Equipamento teste",
            group=EQUIPAMENTO,
        )

        self.unit = Unit.objects.create(
            unit="h",
        )

    def test_get_collection_of_equipmentitem_returns_items_by_id(self):
        equipment = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.item,
            generic_description=self.description,
            input_group=EQUIPAMENTO,
            input_quantity=Decimal("1.00000"),
            input_use=Decimal("0.50000"),
            unit=self.unit,
        )

        collection = InputEquipmentPreparer().get_collection_of_equipmentitem(
            source_file=self.source_file,
        )

        self.assertIn(
            equipment.pk,
            collection,
        )

        self.assertEqual(
            collection[equipment.pk].pk,
            equipment.pk,
        )

    def test_relate_with_source_file_creates_many_to_many_relationship(self):
        equipment = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.item,
            generic_description=self.description,
            input_group=EQUIPAMENTO,
            input_quantity=Decimal("1.00000"),
            input_use=Decimal("0.50000"),
            unit=self.unit,
        )

        preparer = InputEquipmentPreparer()

        preparer.relate_with_source_file(
            equipments=[equipment.pk],
            source_file=self.source_file,
        )

        self.assertIn(
            self.source_file,
            equipment.source_files.all(),
        )

    def test_relate_with_source_file_is_idempotent(self):
        equipment = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=self.item,
            generic_description=self.description,
            input_group=EQUIPAMENTO,
            input_quantity=Decimal("1.00000"),
            input_use=Decimal("0.50000"),
            unit=self.unit,
        )

        preparer = InputEquipmentPreparer()

        preparer.relate_with_source_file(
            equipments=[equipment.pk],
            source_file=self.source_file,
        )

        preparer.relate_with_source_file(
            equipments=[equipment.pk],
            source_file=self.source_file,
        )

        self.assertEqual(
            equipment.source_files.filter(
                pk=self.source_file.pk
            ).count(),
            1,
        )

    def test_create_instances_creates_items_and_source_relationship(self):
        preparer = InputEquipmentPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.item,
            description=self.description,
            group=EQUIPAMENTO,
            quantity=Decimal("1.00000"),
            use=Decimal("0.50000"),
            unit=self.unit,
        )

        preparer.create_instances(
            source_file=self.source_file,
        )

        equipment = EquipmentItem.objects.get(
            composition=self.composition,
            generic_item=self.item,
        )

        self.assertEqual(
            equipment.input_quantity,
            Decimal("1.00000"),
        )

        self.assertEqual(
            equipment.input_use,
            Decimal("0.50000"),
        )

        self.assertIn(
            self.source_file,
            equipment.source_files.all(),
        )


# ============================================================================
# WORKMAN
# ============================================================================

class InputWorkmanPersistenceTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file(
            type_file=MAODEOBRA,
        )

        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="1000002"
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição mão de obra",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m"
            ),
            fic=Decimal("0.00000"),
            production=Decimal("10.00000"),
            composition_group="20",
        )

        self.composition.source_files.add(
            self.source_file
        )

        self.item = GenericItem.objects.create(
            code="P9821",
        )

        self.description = GenericDescription.objects.create(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        self.unit = Unit.objects.create(
            unit="h",
        )

    def test_create_instances_creates_workman_and_relationship(self):
        preparer = InputWorkmanPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.item,
            description=self.description,
            group=MAODEOBRA,
            quantity=Decimal("2.00000"),
            unit=self.unit,
        )

        preparer.create_instances(
            source_file=self.source_file,
        )

        workman = WorkmanItem.objects.get(
            composition=self.composition,
            generic_item=self.item,
        )

        self.assertEqual(
            workman.input_quantity,
            Decimal("2.00000"),
        )

        self.assertEqual(
            workman.unit,
            self.unit,
        )

        self.assertIn(
            self.source_file,
            workman.source_files.all(),
        )

    def test_relate_with_source_file_is_idempotent(self):
        workman = WorkmanItem.objects.create(
            composition=self.composition,
            generic_item=self.item,
            generic_description=self.description,
            input_group=MAODEOBRA,
            input_quantity=Decimal("2.00000"),
            unit=self.unit,
        )

        preparer = InputWorkmanPreparer()

        preparer.relate_with_source_file(
            workmen=[workman.pk],
            source_file=self.source_file,
        )

        preparer.relate_with_source_file(
            workmen=[workman.pk],
            source_file=self.source_file,
        )

        self.assertEqual(
            workman.source_files.filter(
                pk=self.source_file.pk
            ).count(),
            1,
        )


# ============================================================================
# MATERIAL
# ============================================================================

class InputMaterialPersistenceTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file(
            type_file=MATERIAL,
        )

        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="1000003"
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição material",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m"
            ),
            fic=Decimal("0.00000"),
            production=Decimal("10.00000"),
            composition_group="20",
        )

        self.composition.source_files.add(
            self.source_file
        )

        self.item = GenericItem.objects.create(
            code="M1001",
        )

        self.description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        self.unit = Unit.objects.create(
            unit="kg",
        )

    def test_create_instances_creates_material_and_relationship(self):
        preparer = InputMaterialPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.item,
            description=self.description,
            group=MATERIAL,
            quantity=Decimal("50.00000"),
            unit=self.unit,
        )

        preparer.create_instances(
            source_file=self.source_file,
        )

        material = MaterialItem.objects.get(
            composition=self.composition,
            generic_item=self.item,
        )

        self.assertEqual(
            material.input_quantity,
            Decimal("50.00000"),
        )

        self.assertEqual(
            material.unit,
            self.unit,
        )

        self.assertIn(
            self.source_file,
            material.source_files.all(),
        )

    def test_relate_with_source_file_is_idempotent(self):
        material = MaterialItem.objects.create(
            composition=self.composition,
            generic_item=self.item,
            generic_description=self.description,
            input_group=MATERIAL,
            input_quantity=Decimal("50.00000"),
            unit=self.unit,
        )

        preparer = InputMaterialPreparer()

        preparer.relate_with_source_file(
            materials=[material.pk],
            source_file=self.source_file,
        )

        preparer.relate_with_source_file(
            materials=[material.pk],
            source_file=self.source_file,
        )

        self.assertEqual(
            material.source_files.filter(
                pk=self.source_file.pk
            ).count(),
            1,
        )


# ============================================================================
# ATIVIDADE AUXILIAR
# ============================================================================

class InputAuxiliaryActivityPersistenceTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file(
            type_file=ANALITICO,
        )

        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="1000004"
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição auxiliar",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m"
            ),
            fic=Decimal("0.00000"),
            production=Decimal("10.00000"),
            composition_group="20",
        )

        self.composition.source_files.add(
            self.source_file
        )

        self.item = GenericItem.objects.create(
            code="1107928",
        )

        self.description = GenericDescription.objects.create(
            description="Concreto teste",
            group=COMPOSICAO,
        )

        self.unit = Unit.objects.create(
            unit="m3",
        )

    def test_create_instances_creates_auxiliary_activity_and_relationship(self):
        preparer = InputAuxiliaryActivityPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.item,
            description=self.description,
            group=AUXILIAR,
            quantity=Decimal("0.13900"),
            unit=self.unit,
        )

        preparer.create_instances(
            source_file=self.source_file,
        )

        activity = AuxiliaryActivityItem.objects.get(
            composition=self.composition,
            generic_item=self.item,
        )

        self.assertEqual(
            activity.input_quantity,
            Decimal("0.13900"),
        )

        self.assertEqual(
            activity.input_group,
            AUXILIAR,
        )

        self.assertIn(
            self.source_file,
            activity.source_files.all(),
        )


# ============================================================================
# TRANSPORTE
# ============================================================================

class InputTransportPersistenceTests(TestCase):

    def setUp(self):
        self.source_file = create_source_file(
            type_file=ANALITICO,
        )

        self.composition = Composition.objects.create(
            generic_item=GenericItem.objects.create(
                code="1000005"
            ),
            generic_description=GenericDescription.objects.create(
                description="Composição transporte",
                group=COMPOSICAO,
            ),
            unit=Unit.objects.create(
                unit="m"
            ),
            fic=Decimal("0.00000"),
            production=Decimal("10.00000"),
            composition_group="20",
        )

        self.composition.source_files.add(
            self.source_file
        )

        self.item = GenericItem.objects.create(
            code="5914569",
        )

        self.description = GenericDescription.objects.create(
            description="Transporte rodoviário",
            group=COMPOSICAO,
        )

        self.proprietary = GenericItem.objects.create(
            code="1107928",
        )

        self.unit = Unit.objects.create(
            unit="tkm",
        )

    def test_create_instances_creates_transport_and_relationship(self):
        preparer = InputTransportPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.item,
            description=self.description,
            group=PAVIMENTADO,
            quantity=Decimal("0.33360"),
            unit=self.unit,
            proprietary=self.proprietary,
        )

        preparer.create_instances(
            source_file=self.source_file,
        )

        transport = TransportItem.objects.get(
            composition=self.composition,
            generic_item=self.item,
        )

        self.assertEqual(
            transport.input_quantity,
            Decimal("0.33360"),
        )

        self.assertEqual(
            transport.input_group,
            PAVIMENTADO,
        )

        self.assertEqual(
            transport.proprietary_item,
            self.proprietary,
        )

        self.assertIn(
            self.source_file,
            transport.source_files.all(),
        )

    def test_relate_with_source_file_is_idempotent(self):
        transport = TransportItem.objects.create(
            composition=self.composition,
            generic_item=self.item,
            generic_description=self.description,
            input_group=PAVIMENTADO,
            input_quantity=Decimal("0.33360"),
            unit=self.unit,
            proprietary_item=self.proprietary,
        )

        preparer = InputTransportPreparer()

        preparer.relate_with_source_file(
            transports=[transport.pk],
            source_file=self.source_file,
        )

        preparer.relate_with_source_file(
            transports=[transport.pk],
            source_file=self.source_file,
        )

        self.assertEqual(
            transport.source_files.filter(
                pk=self.source_file.pk
            ).count(),
            1,
        )


# ============================================================================
# TERCEIRO BLOCO — CASOS-LIMITE E REGRAS ESTRUTURAIS
# ============================================================================


class DataStructureEdgeCaseTests(TestCase):
    """
    Testes de casos-limite dos preparadores de data_structure.py.

    Objetivo:
        Verificar comportamentos que não são cobertos pelos testes básicos,
        especialmente precisão, valores nulos, múltiplas chamadas e
        preservação da estrutura dos dados.

    Estes testes NÃO alteram os Models.
    """

    def create_source_file(
        self,
        *,
        type_file=MATERIAL,
        data_base=date(2023, 7, 1),
    ):
        return SourceFile.objects.create(
            data_base=data_base,
            source_file="teste.xlsx",
            type_file=type_file,
            type_system=ONERADO,
            methodology=SICRO,
            uf=GOIAS,
        )

    # ------------------------------------------------------------------------
    # COMPOSITION PREPARER
    # ------------------------------------------------------------------------

    def test_composition_preparer_preserves_decimal_precision(self):
        """
        Valores de produção e FIC devem chegar ao Model preservando
        as cinco casas decimais suportadas pela estrutura.
        """

        preparer = CompositionPreparer()

        item = GenericItem.objects.create(
            code="1100001",
        )

        description = GenericDescription.objects.create(
            description="Composição de teste",
            group=COMPOSICAO,
        )

        unit = Unit.objects.create(
            unit="m",
        )

        preparer.append_code(item)
        preparer.append_description(description)
        preparer.append_production(Decimal("24.63001"))
        preparer.append_unit(unit)
        preparer.append_fic(Decimal("0.12345"))
        preparer.append_group("20")

        objects = preparer.get_bulk_create_list()

        self.assertEqual(
            len(objects),
            1,
        )

        composition = objects[0]

        self.assertEqual(
            composition.generic_item,
            item,
        )

        self.assertEqual(
            composition.generic_description,
            description,
        )

        self.assertEqual(
            composition.production,
            Decimal("24.63001"),
        )

        self.assertEqual(
            composition.fic,
            Decimal("0.12345"),
        )

    def test_composition_preparer_preserves_order(self):
        """
        A ordem dos códigos adicionados deve ser preservada.
        """

        preparer = CompositionPreparer()

        item_1 = GenericItem.objects.create(
            code="1100001",
        )

        item_2 = GenericItem.objects.create(
            code="1100002",
        )

        description_1 = GenericDescription.objects.create(
            description="Primeira",
            group=COMPOSICAO,
        )

        description_2 = GenericDescription.objects.create(
            description="Segunda",
            group=COMPOSICAO,
        )

        unit = Unit.objects.create(
            unit="m",
        )

        preparer.append_code(item_1)
        preparer.append_description(description_1)
        preparer.append_production(Decimal("10"))
        preparer.append_unit(unit)
        preparer.append_fic(Decimal("0"))
        preparer.append_group("20")

        preparer.append_code(item_2)
        preparer.append_description(description_2)
        preparer.append_production(Decimal("20"))
        preparer.append_unit(unit)
        preparer.append_fic(Decimal("0.1"))
        preparer.append_group("20")

        objects = preparer.get_bulk_create_list()

        self.assertEqual(
            len(objects),
            2,
        )

        self.assertEqual(
            objects[0].generic_item,
            item_1,
        )

        self.assertEqual(
            objects[1].generic_item,
            item_2,
        )

        self.assertEqual(
            objects[0].generic_description,
            description_1,
        )

        self.assertEqual(
            objects[1].generic_description,
            description_2,
        )

    def test_composition_preparer_empty_returns_empty_list(self):
        """
        Um preparador novo não deve gerar objetos.
        """

        preparer = CompositionPreparer()

        objects = preparer.get_bulk_create_list()

        self.assertEqual(
            objects,
            [],
        )


# ============================================================================
# PREPARADORES DE INSUMOS — VALORES DECIMAIS
# ============================================================================


class InputPreparerDecimalTests(TestCase):
    """
    Verifica preservação dos valores quantitativos dos insumos.
    """

    def setUp(self):
        self.source_file = SourceFile.objects.create(
            data_base=date(2023, 7, 1),
            source_file="teste.xlsx",
            type_file=ANALITICO,
            type_system=ONERADO,
            methodology=SICRO,
            uf=GOIAS,
        )

        self.composition_item = GenericItem.objects.create(
            code="1100001",
        )

        self.composition_description = GenericDescription.objects.create(
            description="Composição de teste",
            group=COMPOSICAO,
        )

        self.unit_m = Unit.objects.create(
            unit="m",
        )

        self.unit_h = Unit.objects.create(
            unit="h",
        )

        self.composition = Composition.objects.create(
            generic_item=self.composition_item,
            generic_description=self.composition_description,
            unit=self.unit_m,
            fic=Decimal("0.00000"),
            production=Decimal("24.63000"),
            composition_group="20",
        )

    def test_equipment_preserves_quantity_and_use(self):
        """
        Equipamento deve preservar quantidade e utilização.
        """

        item = GenericItem.objects.create(
            code="E9102",
        )

        description = GenericDescription.objects.create(
            description="Extrusora",
            group=EQUIPAMENTO,
        )

        preparer = InputEquipmentPreparer()

        preparer.append_input(
            composition=self.composition,
            code=item,
            description=description,
            group=EQUIPAMENTO,
            quantity=Decimal("1.23456"),
            use=Decimal("0.98765"),
            unit=self.unit_h,
        )

        preparer.get_bulk_create_list()

        equipment = EquipmentItem.objects.get(
            composition=self.composition,
            generic_item=item,
        )

        self.assertEqual(
            equipment.input_quantity,
            Decimal("1.23456"),
        )

        self.assertEqual(
            equipment.input_use,
            Decimal("0.98765"),
        )

    def test_workman_preserves_quantity(self):
        """
        Mão de obra deve preservar quantidade.
        """

        item = GenericItem.objects.create(
            code="P9821",
        )

        description = GenericDescription.objects.create(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        preparer = InputWorkmanPreparer()

        preparer.append_input(
            composition=self.composition,
            code=item,
            description=description,
            group=MAODEOBRA,
            quantity=Decimal("2.34567"),
            unit=self.unit_h,
        )

        preparer.get_bulk_create_list()

        workman = WorkmanItem.objects.get(
            composition=self.composition,
            generic_item=item,
        )

        self.assertEqual(
            workman.input_quantity,
            Decimal("2.34567"),
        )

    def test_material_preserves_quantity(self):
        """
        Material deve preservar quantidade.
        """

        item = GenericItem.objects.create(
            code="M1001",
        )

        description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

        preparer = InputMaterialPreparer()

        preparer.append_input(
            composition=self.composition,
            code=item,
            description=description,
            group=MATERIAL,
            quantity=Decimal("0.13900"),
            unit=self.unit_m,
        )

        preparer.get_bulk_create_list()

        material = MaterialItem.objects.get(
            composition=self.composition,
            generic_item=item,
        )

        self.assertEqual(
            material.input_quantity,
            Decimal("0.13900"),
        )

    def test_auxiliary_activity_preserves_quantity(self):
        """
        Atividade auxiliar deve preservar quantidade.
        """

        item = GenericItem.objects.create(
            code="1107928",
        )

        description = GenericDescription.objects.create(
            description="Concreto",
            group=MATERIAL,
        )

        preparer = InputAuxiliaryActivityPreparer()

        preparer.append_input(
            composition=self.composition,
            code=item,
            description=description,
            group=AUXILIAR,
            quantity=Decimal("0.13900"),
            unit=self.unit_m,
        )

        preparer.get_bulk_create_list()

        activity = AuxiliaryActivityItem.objects.get(
            composition=self.composition,
            generic_item=item,
        )

        self.assertEqual(
            activity.input_quantity,
            Decimal("0.13900"),
        )


# ============================================================================
# TRANSPORT PREPARER — PROPRIETARY ITEM
# ============================================================================


class InputTransportEdgeCaseTests(TestCase):

    def setUp(self):
        self.unit_tkm = Unit.objects.create(
            unit="tkm",
        )

        self.composition_item = GenericItem.objects.create(
            code="2003979",
        )

        self.composition_description = GenericDescription.objects.create(
            description="Sarjeta de teste",
            group=COMPOSICAO,
        )

        self.composition = Composition.objects.create(
            generic_item=self.composition_item,
            generic_description=self.composition_description,
            unit=self.unit_tkm,
            fic=Decimal("0"),
            production=Decimal("24.63000"),
            composition_group="20",
        )

        self.transport_item = GenericItem.objects.create(
            code="5919534",
        )

        self.transport_description = GenericDescription.objects.create(
            description="Carga, manobra e descarga",
            group=EQUIPAMENTO,
        )

        self.proprietary_item = GenericItem.objects.create(
            code="1107928",
        )

    def test_transport_preserves_proprietary_item(self):
        """
        O vínculo com o insumo proprietário deve ser preservado.
        """

        preparer = InputTransportPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.transport_item,
            description=self.transport_description,
            group=TEMPO_FIXO,
            quantity=Decimal("0.33360"),
            unit=self.unit_tkm,
            proprietary=self.proprietary_item,
        )

        preparer.get_bulk_create_list()

        transport = TransportItem.objects.get(
            composition=self.composition,
            generic_item=self.transport_item,
        )

        self.assertEqual(
            transport.proprietary_item,
            self.proprietary_item,
        )

        self.assertEqual(
            transport.input_quantity,
            Decimal("0.33360"),
        )


# ============================================================================
# IDEMPOTÊNCIA DOS PREPARADORES DE INSUMOS
# ============================================================================


class InputPreparerRepeatedCallTests(TestCase):
    """
    Verifica o comportamento quando get_bulk_create_list() é chamado
    repetidamente.

    IMPORTANTE:

        O teste documenta o comportamento atual.
        Não pressupõe alteração do código de produção.
    """

    def setUp(self):
        self.composition_item = GenericItem.objects.create(
            code="1100001",
        )

        self.composition_description = GenericDescription.objects.create(
            description="Composição",
            group=COMPOSICAO,
        )

        self.unit = Unit.objects.create(
            unit="m",
        )

        self.composition = Composition.objects.create(
            generic_item=self.composition_item,
            generic_description=self.composition_description,
            unit=self.unit,
            fic=Decimal("0"),
            production=Decimal("10"),
            composition_group="20",
        )

        self.item = GenericItem.objects.create(
            code="M1001",
        )

        self.description = GenericDescription.objects.create(
            description="Cimento",
            group=MATERIAL,
        )

    def test_material_get_bulk_create_list_second_call_does_not_change_database_count(self):
        """
        O segundo processamento com os mesmos dados deve continuar
        protegido pela constraint do Model.
        """

        preparer = InputMaterialPreparer()

        preparer.append_input(
            composition=self.composition,
            code=self.item,
            description=self.description,
            group=MATERIAL,
            quantity=Decimal("1.00000"),
            unit=self.unit,
        )

        preparer.get_bulk_create_list()

        first_count = MaterialItem.objects.count()

        preparer.get_bulk_create_list()

        second_count = MaterialItem.objects.count()

        self.assertEqual(
            first_count,
            1,
        )

        self.assertEqual(
            second_count,
            first_count,
        )


# ============================================================================
# REGRA ESTRUTURAL — MESMO CÓDIGO, DIFERENTES COMPOSIÇÕES
# ============================================================================


class CompositionStructuralIdentityTests(TestCase):
    """
    Testes da identidade estrutural de Composition.

    A regra importante aqui é:

        generic_item
        + unit
        + fic
        + production
        + composition_group

    formam a identidade estrutural protegida pela constraint do Model.

    Portanto, o mesmo código pode representar mais de uma Composition
    quando esses dados forem diferentes.
    """

    def setUp(self):
        self.item = GenericItem.objects.create(
            code="2003979",
        )

        self.description = GenericDescription.objects.create(
            description="Sarjeta trapezoidal",
            group=COMPOSICAO,
        )

        self.unit_m = Unit.objects.create(
            unit="m",
        )

    def test_same_code_different_production_creates_distinct_compositions(self):
        """
        Mesmo código + mesma unidade + mesmo FIC + mesmo grupo,
        mas produção diferente:

            deve permitir duas Composition distintas.
        """

        Composition.objects.create(
            generic_item=self.item,
            generic_description=self.description,
            unit=self.unit_m,
            fic=Decimal("0"),
            production=Decimal("24.63000"),
            composition_group="20",
        )

        Composition.objects.create(
            generic_item=self.item,
            generic_description=self.description,
            unit=self.unit_m,
            fic=Decimal("0"),
            production=Decimal("30.00000"),
            composition_group="20",
        )

        compositions = Composition.objects.filter(
            generic_item=self.item,
        )

        self.assertEqual(
            compositions.count(),
            2,
        )

    def test_same_structural_data_cannot_create_duplicate_composition(self):
        """
        Dados estruturais completamente iguais devem respeitar
        a constraint unique_composition.
        """

        Composition.objects.create(
            generic_item=self.item,
            generic_description=self.description,
            unit=self.unit_m,
            fic=Decimal("0"),
            production=Decimal("24.63000"),
            composition_group="20",
        )

        with self.assertRaises(Exception):
            Composition.objects.create(
                generic_item=self.item,
                generic_description=self.description,
                unit=self.unit_m,
                fic=Decimal("0"),
                production=Decimal("24.63000"),
                composition_group="20",
            )

    def test_same_code_can_have_different_fic(self):
        """
        Mesmo código, mas FIC diferente, deve representar
        estruturas distintas.
        """

        Composition.objects.create(
            generic_item=self.item,
            generic_description=self.description,
            unit=self.unit_m,
            fic=Decimal("0"),
            production=Decimal("24.63000"),
            composition_group="20",
        )

        Composition.objects.create(
            generic_item=self.item,
            generic_description=self.description,
            unit=self.unit_m,
            fic=Decimal("0.10000"),
            production=Decimal("24.63000"),
            composition_group="20",
        )

        self.assertEqual(
            Composition.objects.filter(
                generic_item=self.item,
            ).count(),
            2,
        )