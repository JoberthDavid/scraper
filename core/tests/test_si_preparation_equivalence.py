from io import BytesIO
from unittest import TestCase

import pandas as pd
from pandas.testing import assert_frame_equal

from core.usefuls.si_validator import (
    SI_COLUMNS,
    prepare_si_dataframe,
)


class SIPreparationEquivalenceTests(TestCase):

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

    def build_independent_reference(self, xlsx_content):
        """
        Builds an expected SI DataFrame independently from
        prepare_si_dataframe().

        This intentionally does not use:
            - prepare_si_dataframe()
            - prepare_dataframe_from_xlsx()
            - is_si_data_row()
        """

        raw_dataframe = pd.read_excel(
            BytesIO(xlsx_content),
            header=None,
        )

        first_data_row = None

        for index, row in raw_dataframe.iterrows():

            if len(row) < 4:
                continue

            code = row.iloc[0]
            description = row.iloc[1]
            unit = row.iloc[2]
            monetary_value = row.iloc[3]

            if pd.isna(code):
                continue

            code = str(code).strip()

            if (
                not code.isdigit()
                or len(code) != 7
            ):
                continue

            if (
                pd.isna(description)
                or not str(description).strip()
            ):
                continue

            if (
                pd.isna(unit)
                or not str(unit).strip()
            ):
                continue

            try:
                float(
                    str(
                        monetary_value
                    ).strip()
                )
            except (TypeError, ValueError):
                continue

            first_data_row = index
            break

        if first_data_row is None:
            raise ValueError(
                "Independent reference could not "
                "find the first SI data row."
            )

        expected = (
            raw_dataframe
            .iloc[first_data_row:, :4]
            .copy()
            .reset_index(drop=True)
        )

        expected.columns = list(
            SI_COLUMNS
        )

        expected["code"] = (
            expected["code"]
            .astype("string")
            .str.strip()
        )

        expected["description"] = (
            expected["description"]
            .astype("string")
            .str.strip()
        )

        expected["unit"] = (
            expected["unit"]
            .astype("string")
            .str.strip()
        )

        expected["monetary_value"] = (
            pd.to_numeric(
                expected["monetary_value"],
                errors="raise",
            )
            .astype("float64")
        )

        return expected, first_data_row

    # ==================================================================
    # TEST DATA
    # ==================================================================

    def valid_rows(self):
        return [
            [
                "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS",
                "",
                "",
                "",
            ],
            [
                "Cabeçalho",
                "",
                "",
                "",
            ],
            [
                "0307731",
                "  Composição A  ",
                " m3 ",
                123.4567,
            ],
            [
                "0307732",
                "Composição B",
                "m2",
                234.5678,
            ],
            [
                "0307733",
                "Composição C",
                "kg",
                345.6789,
            ],
        ]

    # ==================================================================
    # EQUIVALENCE — STRUCTURE
    # ==================================================================

    def test_prepared_dataframe_has_same_shape_as_independent_reference(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertEqual(
            prepared.data_frame.shape,
            expected.shape,
        )

    def test_prepared_dataframe_has_same_columns_as_independent_reference(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertEqual(
            list(prepared.data_frame.columns),
            list(expected.columns),
        )

    # ==================================================================
    # EQUIVALENCE — TEXT
    # ==================================================================

    def test_prepared_codes_match_independent_reference(self):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertEqual(
            prepared.data_frame["code"].tolist(),
            expected["code"].tolist(),
        )

    def test_prepared_descriptions_match_independent_reference(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertEqual(
            prepared.data_frame[
                "description"
            ].tolist(),
            expected["description"].tolist(),
        )

    def test_prepared_units_match_independent_reference(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertEqual(
            prepared.data_frame["unit"].tolist(),
            expected["unit"].tolist(),
        )

    # ==================================================================
    # EQUIVALENCE — NUMERIC
    # ==================================================================

    def test_prepared_monetary_values_match_independent_reference(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertTrue(
            (
                prepared.data_frame[
                    "monetary_value"
                ]
                == expected[
                    "monetary_value"
                ]
            ).all()
        )

    def test_prepared_monetary_column_has_same_dtype(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertEqual(
            prepared.data_frame[
                "monetary_value"
            ].dtype,
            expected[
                "monetary_value"
            ].dtype,
        )

    # ==================================================================
    # EQUIVALENCE — COMPLETE DATAFRAME
    # ==================================================================

    def test_prepared_dataframe_matches_independent_reference(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        assert_frame_equal(
            prepared.data_frame.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_dtype=True,
            check_exact=True,
        )

    # ==================================================================
    # FIRST DATA ROW
    # ==================================================================

    def test_first_data_row_matches_independent_reference(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        _, expected_first_data_row = (
            self.build_independent_reference(
                xlsx_content
            )
        )

        self.assertEqual(
            prepared.first_data_row,
            expected_first_data_row,
        )

    # ==================================================================
    # VALIDATION
    # ==================================================================

    def test_equivalent_dataframe_passes_validation(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes(
            self.valid_rows()
        )

        prepared = prepare_si_dataframe(
            xlsx_content
        )

        self.assertTrue(
            prepared.validation.valid
        )

        self.assertEqual(
            prepared.validation.errors,
            (),
        )
