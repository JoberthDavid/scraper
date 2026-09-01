from io import BytesIO
from unittest import TestCase

import pandas as pd
from pandas.testing import assert_frame_equal

from core.usefuls.choices import (
    SINTETICO,
    MATERIAL,
    MAODEOBRA,
    EQUIPAMENTO,
)

from core.usefuls.synthetic_validator import (
    prepare_synthetic_dataframe,
)


class SyntheticPreparersEquivalenceTests(TestCase):

    # ==================================================================
    # XLSX CREATION
    # ==================================================================

    def create_xlsx_bytes(self, rows):
        dataframe = pd.DataFrame(rows)

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl",
        ) as writer:
            dataframe.to_excel(
                writer,
                header=False,
                index=False,
            )

        return buffer.getvalue()

    # ==================================================================
    # INDEPENDENT REFERENCE
    # ==================================================================

    def build_reference_dataframe(
        self,
        xlsx_content,
        *,
        first_data_row,
        columns,
        numeric_columns,
    ):
        """
        Builds the expected DataFrame independently from
        prepare_synthetic_dataframe().

        This function deliberately does not use:
            - prepare_synthetic_dataframe()
            - prepare_dataframe_from_xlsx()
            - ROW_VALIDATORS
            - any synthetic preparer implementation
        """

        raw_dataframe = pd.read_excel(
            BytesIO(xlsx_content),
            header=None,
        )

        expected = (
            raw_dataframe
            .iloc[first_data_row:]
            .copy()
            .reset_index(drop=True)
        )

        expected = expected.iloc[
            :,
            :len(columns),
        ].copy()

        expected.columns = list(columns)

        for column in (
            "code",
            "description",
        ):
            if column in expected.columns:
                expected[column] = (
                    expected[column]
                    .astype("string")
                    .str.strip()
                )

        for column in (
            "code",
            "description",
        ):
            if column in expected.columns:
                expected[column] = (
                    expected[column]
                    .astype("string")
                    .str.strip()
                )

        if "unit" in expected.columns:

            if columns[-1] == "unit" and len(columns) == 12:
                expected["unit"] = (
                    expected["unit"]
                    .map(
                        lambda value: (
                            str(value).strip()
                            if not pd.isna(value)
                            else value
                        )
                    )
                )

            else:
                expected["unit"] = (
                    expected["unit"]
                    .astype("string")
                    .str.strip()
                )

        for column in numeric_columns:
            expected[column] = pd.to_numeric(
                expected[column],
                errors="raise",
            )

        return expected

    # ==================================================================
    # SI
    # ==================================================================

    def si_rows(self):
        return [
            [
                "Cabeçalho SI",
                "",
                "",
                "",
            ],
            [
                "0307731",
                "  Composição SI A  ",
                " m3 ",
                123.4567,
            ],
            [
                "0307732",
                "Composição SI B",
                "kg",
                234.5678,
            ],
        ]

    def test_si_preparer_matches_independent_reference(self):
        xlsx_content = self.create_xlsx_bytes(
            self.si_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=SINTETICO,
        )

        expected = self.build_reference_dataframe(
            xlsx_content,
            first_data_row=1,
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
            numeric_columns=[
                "monetary_value",
            ],
        )

        assert_frame_equal(
            result.data_frame.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_dtype=True,
            check_exact=True,
        )

    def test_si_preparer_detects_correct_first_data_row(self):
        xlsx_content = self.create_xlsx_bytes(
            self.si_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=SINTETICO,
        )

        self.assertEqual(
            result.detection.first_data_row,
            1,
        )



    # ==================================================================
    # MATERIAL
    # ==================================================================

    def material_rows(self):
        return [
            [
                "Cabeçalho MATERIAL",
                "",
                "",
                "",
            ],
            [
                "M1001",
                "  Cimento  ",
                " kg ",
                12.3456,
            ],
            [
                "M1002",
                "Areia",
                "m3",
                23.4567,
            ],
        ]

    def test_material_preparer_matches_independent_reference(self):
        xlsx_content = self.create_xlsx_bytes(
            self.material_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=MATERIAL,
        )

        expected = self.build_reference_dataframe(
            xlsx_content,
            first_data_row=1,
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
            numeric_columns=[
                "monetary_value",
            ],
        )

        assert_frame_equal(
            result.data_frame.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_dtype=True,
            check_exact=True,
        )

    def test_material_preparer_detects_correct_first_data_row(self):
        xlsx_content = self.create_xlsx_bytes(
            self.material_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=MATERIAL,
        )

        self.assertEqual(
            result.detection.first_data_row,
            1,
        )

  

    # ==================================================================
    # WORKMAN
    # ==================================================================

    def workman_rows(self):
        return [
            [
                "Cabeçalho MO",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "P1001",
                "  Pedreiro  ",
                " h ",
                20.0,
                3.5,
                35.6789,
                0.0,
            ],
            [
                "P1002",
                "Servente",
                "h",
                18.0,
                2.5,
                28.4567,
                0.0,
            ],
        ]

    def test_workman_preparer_matches_independent_reference(self):
        xlsx_content = self.create_xlsx_bytes(
            self.workman_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=MAODEOBRA,
        )

        expected = self.build_reference_dataframe(
            xlsx_content,
            first_data_row=1,
            columns=[
                "code",
                "description",
                "unit",
                "wage",
                "charges",
                "monetary_value",
                "unhealthy",
            ],
            numeric_columns=[
                "wage",
                "charges",
                "monetary_value",
                "unhealthy",
            ],
        )

        assert_frame_equal(
            result.data_frame.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_dtype=True,
            check_exact=True,
        )

    def test_workman_preparer_detects_correct_first_data_row(self):
        xlsx_content = self.create_xlsx_bytes(
            self.workman_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=MAODEOBRA,
        )

        self.assertEqual(
            result.detection.first_data_row,
            1,
        )

 

    # ==================================================================
    # EQUIPMENT
    # ==================================================================

    def equipment_rows(self):
        return [
            [
                "Cabeçalho EQ",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "E1001",
                "  Escavadeira  ",
                100.0,
                10.0,
                5.0,
                2.0,
                3.0,
                4.0,
                5.0,
                42.1930,
                28.0238,
                "h",
            ],
            [
                "A1001",
                "Caminhão",
                200.0,
                20.0,
                10.0,
                3.0,
                4.0,
                5.0,
                6.0,
                52.4567,
                31.2345,
                "h",
            ],
        ]

    def test_equipment_preparer_matches_independent_reference(self):
        xlsx_content = self.create_xlsx_bytes(
            self.equipment_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=EQUIPAMENTO,
        )

        expected = self.build_reference_dataframe(
            xlsx_content,
            first_data_row=1,
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
                "unit",
            ],
            numeric_columns=[
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

        assert_frame_equal(
            result.data_frame.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_dtype=True,
            check_exact=True,
        )

    def test_equipment_preparer_detects_correct_first_data_row(self):
        xlsx_content = self.create_xlsx_bytes(
            self.equipment_rows()
        )

        result = prepare_synthetic_dataframe(
            xlsx_content=xlsx_content,
            type_file=EQUIPAMENTO,
        )

        self.assertEqual(
            result.detection.first_data_row,
            1,
        )