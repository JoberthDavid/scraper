from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import (
    SourceFile,
    GenericItem,
    GenericDescription,
    Unit,
    Composition,
    MonetaryValue,
    EquipmentItem,
    WorkmanItem,
    MaterialItem,
    AuxiliaryActivityItem,
    TransportItem,
)

from core.usefuls.choices import (
    SICRO,
    GOIAS,
    DISTRITO_FEDERAL,
    ONERADO,
    DESONERADO,
    ANALITICO,
    SINTETICO,
    EQUIPAMENTO,
    MAODEOBRA,
    MATERIAL,
    COMPOSICAO,
    CUSTO,
    AUXILIAR,
    TEMPO_FIXO,
)


class ViewSetIntegrationTests(TestCase):
    """
    HTTP integration tests for the DRF viewsets.

    These tests verify the complete path:

        HTTP request
            ↓
        ViewSet
            ↓
        Filter
            ↓
        QuerySet
            ↓
        Serializer
            ↓
        HTTP response
    """

    def setUp(self):
        self.client = APIClient()

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
            uf=GOIAS,
            data_base=date(2024, 7, 1),
            source_file="si_2024.xlsx",
            type_system=ONERADO,
            type_file=SINTETICO,
            status=True,
        )

        self.inactive_source = SourceFile.objects.create(
            methodology=SICRO,
            uf=DISTRITO_FEDERAL,
            data_base=date(2025, 7, 1),
            source_file="inactive.xlsx",
            type_system=ONERADO,
            type_file=SINTETICO,
            status=False,
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

        self.unit_tkm = Unit.objects.create(
            unit="tkm",
        )

        self.composition_item = GenericItem.objects.create(
            code="1100001",
        )

        self.composition_description = GenericDescription.objects.create(
            description="Execução de concreto",
            group=COMPOSICAO,
        )

        self.composition_item.source_files.add(
            self.source_2023,
            self.source_2024,
        )

        self.composition_description.source_files.add(
            self.source_2023,
            self.source_2024,
        )

        self.composition_description.generic_items.add(
            self.composition_item,
        )

        self.composition = Composition.objects.create(
            generic_item=self.composition_item,
            generic_description=self.composition_description,
            unit=self.unit_m3,
            fic=Decimal("0.10000"),
            production=Decimal("24.63000"),
            composition_group="11",
        )

        self.composition.source_files.add(
            self.source_2023,
        )

        self.material_item = GenericItem.objects.create(
            code="M1001",
        )

        self.material_description = GenericDescription.objects.create(
            description="Cimento Portland",
            group=MATERIAL,
        )

        self.material_item.source_files.add(
            self.source_2023,
        )

        self.material_description.source_files.add(
            self.source_2023,
        )

        self.material_description.generic_items.add(
            self.material_item,
        )

        self.material_value = MonetaryValue.objects.create(
            generic_item=self.material_item,
            source_file=self.source_2023,
            unit=self.unit_kg,
            monetary_value=Decimal("1.2500"),
            classification=CUSTO,
            group=MATERIAL,
            type_system=ONERADO,
        )

    # =====================================================================
    # SOURCE FILE
    # =====================================================================

    def test_source_file_list_returns_only_active_source_files(self):
        response = self.client.get(
            "/arquivos-base/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_ids = {
            item["id"]
            for item in response.data["results"]
        }

        self.assertIn(
            self.source_2023.id,
            returned_ids,
        )

        self.assertIn(
            self.source_2024.id,
            returned_ids,
        )

        self.assertNotIn(
            self.inactive_source.id,
            returned_ids,
        )

    def test_source_file_filter_by_minimum_year(self):
        response = self.client.get(
            "/arquivos-base/",
            {
                "data_base__year__gte": 2024,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_ids = {
            item["id"]
            for item in response.data["results"]
        }

        self.assertIn(
            self.source_2024.id,
            returned_ids,
        )

        self.assertNotIn(
            self.source_2023.id,
            returned_ids,
        )

    # =====================================================================
    # GENERIC ITEM
    # =====================================================================

    def test_generic_item_list_returns_items(self):
        response = self.client.get(
            "/itens/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_codes = {
            item["code"]
            for item in response.data["results"]
        }

        self.assertIn(
            "1100001",
            returned_codes,
        )

        self.assertIn(
            "M1001",
            returned_codes,
        )

    def test_generic_item_filter_by_code(self):
        response = self.client.get(
            "/itens/",
            {
                "code": "M1",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["code"],
            "M1001",
        )

    # =====================================================================
    # SPECIALIZED GENERIC ITEM ENDPOINTS
    # =====================================================================

    def test_composition_item_endpoint_returns_only_composition_items(self):
        response = self.client.get(
            "/itens-composicoes/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_codes = {
            item["code"]
            for item in response.data["results"]
        }

        self.assertIn(
            "1100001",
            returned_codes,
        )

        self.assertNotIn(
            "M1001",
            returned_codes,
        )

    def test_material_item_endpoint_returns_only_material_items(self):
        response = self.client.get(
            "/itens-materiais/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_codes = {
            item["code"]
            for item in response.data["results"]
        }

        self.assertIn(
            "M1001",
            returned_codes,
        )

        self.assertNotIn(
            "1100001",
            returned_codes,
        )

    def test_equipment_item_endpoint_returns_only_equipment_items(self):
        equipment_item = GenericItem.objects.create(
            code="E1001",
        )

        equipment_description = GenericDescription.objects.create(
            description="Escavadeira",
            group=EQUIPAMENTO,
        )

        equipment_item.source_files.add(
            self.source_2023,
        )

        equipment_description.source_files.add(
            self.source_2023,
        )

        equipment_description.generic_items.add(
            equipment_item,
        )

        response = self.client.get(
            "/itens-equipamentos/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_codes = {
            item["code"]
            for item in response.data["results"]
        }

        self.assertIn(
            "E1001",
            returned_codes,
        )

        self.assertNotIn(
            "M1001",
            returned_codes,
        )

    def test_workman_item_endpoint_returns_only_workman_items(self):
        workman_item = GenericItem.objects.create(
            code="P9821",
        )

        workman_description = GenericDescription.objects.create(
            description="Pedreiro",
            group=MAODEOBRA,
        )

        workman_item.source_files.add(
            self.source_2023,
        )

        workman_description.source_files.add(
            self.source_2023,
        )

        workman_description.generic_items.add(
            workman_item,
        )

        response = self.client.get(
            "/itens-mao-de-obra/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_codes = {
            item["code"]
            for item in response.data["results"]
        }

        self.assertIn(
            "P9821",
            returned_codes,
        )

        self.assertNotIn(
            "M1001",
            returned_codes,
        )

    # =====================================================================
    # UNITS
    # =====================================================================

    def test_unit_endpoint_returns_units(self):
        response = self.client.get(
            "/unidades/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_units = {
            item["unit"]
            for item in response.data["results"]
        }

        self.assertIn(
            "m3",
            returned_units,
        )

        self.assertIn(
            "kg",
            returned_units,
        )

    # =====================================================================
    # MONETARY VALUE
    # =====================================================================

    def test_monetary_value_endpoint_returns_values(self):
        response = self.client.get(
            "/valores-monetarios/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        values = response.data["results"]

        self.assertEqual(
            len(values),
            1,
        )

        self.assertEqual(
            values[0]["generic_item"],
            "M1001",
        )

        self.assertEqual(
            values[0]["unit"],
            "kg",
        )

    def test_monetary_value_filter_by_source_file_date(self):
        """
        The endpoint intends to filter MonetaryValue by source-file
        data_base.

        This test intentionally exercises the exact public API parameter
        currently used by MonetaryValueViewSet.
        """

        response = self.client.get(
            "/valores-monetarios/",
            {
                "source_files__data_base": "2023-07-01",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["generic_item"],
            "M1001",
        )

    # =====================================================================
    # COMPOSITIONS
    # =====================================================================

    def test_composition_endpoint_returns_compositions(self):
        response = self.client.get(
            "/composicoes/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        composition = response.data["results"][0]

        self.assertEqual(
            composition["generic_item"],
            "1100001",
        )

        self.assertEqual(
            composition["composition_group"],
            "11",
        )

        self.assertEqual(
            composition["production"],
            "24.63000",
        )

    def test_composition_filter_by_source_file_date(self):
        response = self.client.get(
            "/composicoes/",
            {
                "source_files__data_base": "2023-07-01",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["generic_item"],
            "1100001",
        )

    # =====================================================================
    # READ-ONLY BEHAVIOR
    # =====================================================================

    def test_api_rejects_post_to_read_only_endpoint(self):
        endpoints = [
            "/arquivos-base/",
            "/itens/",
            "/itens-composicoes/",
            "/itens-equipamentos/",
            "/itens-mao-de-obra/",
            "/itens-materiais/",
            "/unidades/",
            "/valores-monetarios/",
            "/composicoes/",
        ]

        for endpoint in endpoints:
            with self.subTest(
                endpoint=endpoint,
            ):
                response = self.client.post(
                    endpoint,
                    {},
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    403,
                )

    def test_composition_detail_endpoint_returns_nested_input_collections(self):
        equipment_item = GenericItem.objects.create(
            code="E1001",
        )

        equipment_description = GenericDescription.objects.create(
            description="Escavadeira",
            group=EQUIPAMENTO,
        )

        equipment = EquipmentItem.objects.create(
            composition=self.composition,
            generic_item=equipment_item,
            generic_description=equipment_description,
            unit=self.unit_h,
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
            unit=self.unit_h,
            input_quantity=Decimal("1.00000"),
            input_group=MAODEOBRA,
        )

        material_description = self.material_description

        MaterialItem.objects.create(
            composition=self.composition,
            generic_item=self.material_item,
            generic_description=material_description,
            unit=self.unit_kg,
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
            unit=self.unit_m3,
            input_quantity=Decimal("0.13900"),
            input_group=AUXILIAR,
        )

        transport_item = GenericItem.objects.create(
            code="5914569",
        )

        transport_description = GenericDescription.objects.create(
            description="Transporte rodoviário",
            group=COMPOSICAO,
        )

        proprietary_item = activity_item

        TransportItem.objects.create(
            composition=self.composition,
            generic_item=transport_item,
            generic_description=transport_description,
            unit=self.unit_tkm,
            input_quantity=Decimal("0.33360"),
            input_group=TEMPO_FIXO,
            proprietary_item=proprietary_item,
        )

        response = self.client.get(
            f"/composicoes/{self.composition.id}/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.data

        self.assertEqual(
            data["generic_item"],
            "1100001",
        )

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