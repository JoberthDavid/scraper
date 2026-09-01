from io import BytesIO
from unittest import TestCase
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from core.usefuls.si_validator import (
    SI_COLUMNS,
    prepare_si_dataframe,
)


class SISingleReadTests(TestCase):

    # ==================================================================
    # XLSX FIXTURE
    # ==================================================================

    def create_xlsx_bytes(self):
        rows = [
            [
                "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS",
                "",
                "",
                "",
            ],
            [
                "Cabeçalho do arquivo",
                "",
                "",
                "",
            ],
            [
                "0307731",
                "  Composição A  ",
                " m3 ",
                123.456789,
            ],
            [
                "0307732",
                "Composição B",
                "kg",
                234.567891,
            ],
            [
                "0307733",
                "Composição C",
                "m2",
                345.678912,
            ],
        ]

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

    def build_independent_reference(
        self,
        xlsx_content,
    ):
        """
        Builds the reference directly from the XLSX.

        This does not use prepare_si_dataframe() or any of its
        internal helper functions.
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
                float(monetary_value)
            except (TypeError, ValueError):
                continue

            first_data_row = index
            break

        if first_data_row is None:
            raise ValueError(
                "Nenhuma linha SI válida foi encontrada."
            )

        expected = (
            raw_dataframe
            .iloc[first_data_row:, :4]
            .copy()
            .reset_index(drop=True)
        )

        expected.columns = list(SI_COLUMNS)

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
    # SINGLE READ
    # ==================================================================

    def test_prepare_si_dataframe_reads_xlsx_only_once(self):
        xlsx_content = self.create_xlsx_bytes()

        with patch(
            "core.usefuls.xlsx_validator.pd.read_excel",
            wraps=pd.read_excel,
        ) as read_excel:

            result = prepare_si_dataframe(
                xlsx_content,
            )

        self.assertEqual(
            read_excel.call_count,
            1,
        )

        self.assertEqual(
            result.first_data_row,
            2,
        )

    # ==================================================================
    # SINGLE-READ RESULT
    # ==================================================================

    def test_single_read_result_has_expected_shape(self):
        xlsx_content = self.create_xlsx_bytes()

        result = prepare_si_dataframe(
            xlsx_content,
        )

        self.assertEqual(
            result.data_frame.shape,
            (3, 4),
        )

    def test_single_read_result_matches_independent_reference(self):
        xlsx_content = self.create_xlsx_bytes()

        result = prepare_si_dataframe(
            xlsx_content,
        )

        expected, expected_first_data_row = (
            self.build_independent_reference(
                xlsx_content,
            )
        )

        self.assertEqual(
            result.first_data_row,
            expected_first_data_row,
        )

        assert_frame_equal(
            result.data_frame.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_dtype=True,
            check_exact=True,
        )

    # ==================================================================
    # TEXT EQUIVALENCE
    # ==================================================================

    def test_single_read_preserves_textual_fields(self):
        xlsx_content = self.create_xlsx_bytes()

        result = prepare_si_dataframe(
            xlsx_content,
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content,
            )
        )

        for column in (
            "code",
            "description",
            "unit",
        ):
            prepared = (
                result.data_frame[column]
                .astype("string")
                .fillna("<NA>")
                .reset_index(drop=True)
            )

            reference = (
                expected[column]
                .astype("string")
                .fillna("<NA>")
                .reset_index(drop=True)
            )

            self.assertTrue(
                prepared.equals(reference),
                msg=(
                    f"Coluna textual divergente: "
                    f"{column}"
                ),
            )

    # ==================================================================
    # NUMERIC EQUIVALENCE
    # ==================================================================

    def test_single_read_preserves_monetary_values_within_tolerance(
        self,
    ):
        xlsx_content = self.create_xlsx_bytes()

        result = prepare_si_dataframe(
            xlsx_content,
        )

        expected, _ = (
            self.build_independent_reference(
                xlsx_content,
            )
        )

        prepared_money = pd.to_numeric(
            result.data_frame["monetary_value"],
            errors="raise",
        )

        reference_money = pd.to_numeric(
            expected["monetary_value"],
            errors="raise",
        )

        difference = (
            prepared_money - reference_money
        ).abs()

        self.assertTrue(
            (
                difference <= 0.000001
            ).all()
        )
