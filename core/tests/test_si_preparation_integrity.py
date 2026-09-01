from io import BytesIO
from unittest import TestCase

import pandas as pd

from core.usefuls.si_validator import (
    SI_COLUMNS,
    prepare_si_dataframe,
)


def create_xlsx_bytes(rows):
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


class SIPreparationTests(TestCase):

    def valid_rows(self):
        return [
            [
                "Cabeçalho do arquivo",
                "",
                "",
                "",
            ],
            [
                "Outro cabeçalho",
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
        ]

    # ==================================================================
    # BASIC PREPARATION
    # ==================================================================

    def test_first_data_row_is_detected(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            result.first_data_row,
            2,
        )

    def test_prepared_dataframe_has_expected_columns(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            list(result.data_frame.columns),
            list(SI_COLUMNS),
        )

    def test_header_rows_are_removed(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            len(result.data_frame),
            2,
        )

        self.assertEqual(
            result.data_frame.iloc[0]["code"],
            "0307731",
        )

    # ==================================================================
    # TEXT NORMALIZATION
    # ==================================================================

    def test_code_is_trimmed(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            result.data_frame.iloc[0]["code"],
            "0307731",
        )

    def test_description_is_trimmed(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            result.data_frame.iloc[0]["description"],
            "Composição A",
        )

    def test_unit_is_trimmed(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            result.data_frame.iloc[0]["unit"],
            "m3",
        )

    # ==================================================================
    # NUMERIC CONVERSION
    # ==================================================================

    def test_monetary_value_is_numeric(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        value = result.data_frame.iloc[0][
            "monetary_value"
        ]

        self.assertTrue(
            pd.api.types.is_numeric_dtype(
                result.data_frame["monetary_value"]
            )
        )

        self.assertEqual(
            value,
            123.4567,
        )

    def test_monetary_value_uses_float64(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            result.data_frame["monetary_value"].dtype,
            "float64",
        )

    # ==================================================================
    # CONTENT PRESERVATION
    # ==================================================================

    def test_all_data_rows_are_preserved(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertEqual(
            result.data_frame["code"].tolist(),
            [
                "0307731",
                "0307732",
            ],
        )

        self.assertEqual(
            result.data_frame["description"].tolist(),
            [
                "Composição A",
                "Composição B",
            ],
        )

        self.assertEqual(
            result.data_frame["unit"].tolist(),
            [
                "m3",
                "m2",
            ],
        )

    # ==================================================================
    # VALIDATION RESULT
    # ==================================================================

    def test_preparation_returns_validation_result(self):
        result = prepare_si_dataframe(
            create_xlsx_bytes(
                self.valid_rows()
            )
        )

        self.assertTrue(
            result.validation.valid,
        )

        self.assertEqual(
            result.validation.errors,
            (),
        )

    # ==================================================================
    # INVALID INPUT
    # ==================================================================

    def test_invalid_monetary_value_is_rejected(self):
        rows = [
            [
                "0307731",
                "Composição A",
                "m3",
                "valor inválido",
            ],
        ]

        with self.assertRaises(
            ValueError
        ):
            prepare_si_dataframe(
                create_xlsx_bytes(rows)
            )

    def test_missing_data_row_raises_value_error(self):
        rows = [
            [
                "Cabeçalho",
                "",
                "",
                "",
            ],
            [
                "Ainda não é uma linha SI",
                "",
                "",
                "",
            ],
        ]

        with self.assertRaises(
            ValueError
        ):
            prepare_si_dataframe(
                create_xlsx_bytes(rows)
            )
