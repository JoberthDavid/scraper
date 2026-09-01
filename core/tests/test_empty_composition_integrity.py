from decimal import Decimal

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
    COMPOSICAO,
    EQUIPAMENTO,
    MAODEOBRA,
    MATERIAL,
    AUXILIAR,
    TEMPO_FIXO,
)

from core.usefuls.analytical_validator import (
    composition_has_inputs,
)


class EmptyCompositionIntegrityTests(TestCase):
    """
    Tests the structural rule used by the analytical database audit:

    A composition is empty only when it has no input of any supported type:

        EquipmentItem
        WorkmanItem
        MaterialItem
        AuxiliaryActivityItem
        TransportItem

    A composition containing at least one input is not empty.
    """

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

        self.unit_m3 = Unit.objects.create(
            unit="m3",
        )

        self.unit_h = Unit.objects.create(
            unit="h",
        )

        self.unit_kg = Unit.objects.create(
            unit="kg",
        )

    def create_composition(
        self,
        code="1100001",
        description="Execução de concreto",
    ):
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
            unit=self.unit_m3,
            fic=Decimal("0.00000"),
            production=Decimal("1.00000"),
            composition_group=code[:2],
        )

        composition.source_files.add(
            self.source_file,
        )

        return composition

    def create_generic_input(
        self,
        code,
        description,
        group,
    ):
        item = GenericItem.objects.create(
            code=code,
        )

        generic_description = GenericDescription.objects.create(
            description=description,
            group=group,
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

        return item, generic_description

    def composition_has_any_input(self, composition):
        return any(
            [
                EquipmentItem.objects.filter(
                    composition=composition
                ).exists(),
                WorkmanItem.objects.filter(
                    composition=composition
                ).exists(),
                MaterialItem.objects.filter(
                    composition=composition
                ).exists(),
                AuxiliaryActivityItem.objects.filter(
                    composition=composition
                ).exists(),
                TransportItem.objects.filter(
                    composition=composition
                ).exists(),
            ]
        )

    def test_composition_without_inputs_is_detected_as_empty(self):
        composition = self.create_composition()

        self.assertFalse(
            composition_has_inputs(
                composition
            )
        )

    def test_composition_with_equipment_is_not_empty(self):
        composition = self.create_composition(
            code="1100003",
            description="Composição com equipamento",
        )

        item, description = self.create_generic_input(
            code="E1001",
            description="Escavadeira",
            group=EQUIPAMENTO,
        )

        EquipmentItem.objects.create(
            composition=composition,
            generic_item=item,
            generic_description=description,
            unit=self.unit_h,
            input_quantity=Decimal("1.00000"),
            input_use=Decimal("2.00000"),
            input_group=EQUIPAMENTO,
        )

        self.assertTrue(
            composition_has_inputs(
                composition
            )
        )

    def test_composition_with_workman_is_not_empty(self):
        composition = self.create_composition(
            code="1100002",
            description="Composição com mão de obra",
        )

        item, description = self.create_generic_input(
            code="P9821",
            description="Pedreiro",
            group=MAODEOBRA,
        )

        WorkmanItem.objects.create(
            composition=composition,
            generic_item=item,
            generic_description=description,
            unit=self.unit_h,
            input_quantity=Decimal("1.00000"),
            input_group=MAODEOBRA,
        )

        self.assertTrue(
            self.composition_has_any_input(
                composition
            )
        )

    def test_composition_with_material_is_not_empty(self):
        composition = self.create_composition(
            code="1100003",
            description="Composição com material",
        )

        item, description = self.create_generic_input(
            code="M1001",
            description="Cimento",
            group=MATERIAL,
        )

        MaterialItem.objects.create(
            composition=composition,
            generic_item=item,
            generic_description=description,
            unit=self.unit_kg,
            input_quantity=Decimal("2.50000"),
            input_group=MATERIAL,
        )

        self.assertTrue(
            self.composition_has_any_input(
                composition
            )
        )

    def test_composition_with_auxiliary_activity_is_not_empty(self):
        composition = self.create_composition(
            code="1100004",
            description="Composição com atividade auxiliar",
        )

        item, description = self.create_generic_input(
            code="1107928",
            description="Atividade auxiliar",
            group=COMPOSICAO,
        )

        AuxiliaryActivityItem.objects.create(
            composition=composition,
            generic_item=item,
            generic_description=description,
            unit=self.unit_m3,
            input_quantity=Decimal("0.13900"),
            input_group=AUXILIAR,
        )

        self.assertTrue(
            self.composition_has_any_input(
                composition
            )
        )

    def test_composition_with_transport_is_not_empty(self):
        composition = self.create_composition(
            code="1100005",
            description="Composição com transporte",
        )

        item, description = self.create_generic_input(
            code="5914569",
            description="Transporte rodoviário",
            group=COMPOSICAO,
        )

        TransportItem.objects.create(
            composition=composition,
            generic_item=item,
            generic_description=description,
            unit=self.unit_m3,
            input_quantity=Decimal("0.33360"),
            input_group=TEMPO_FIXO,
        )

        self.assertTrue(
            self.composition_has_any_input(
                composition
            )
        )
