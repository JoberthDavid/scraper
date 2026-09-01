from unittest import TestCase

import pandas as pd

from core.usefuls.choices import (
    SINTETICO,
    MATERIAL,
    MAODEOBRA,
    EQUIPAMENTO,
)

from core.usefuls.synthetic_validator import (
    is_text,
    is_numeric,
    is_numeric_or_dash,
    matches_pattern,
    is_si_data_row,
    is_material_data_row,
    is_workman_data_row,
    is_equipment_data_row,
    detect_synthetic_structure,
)


class SyntheticValueDetectorTests(TestCase):

    def test_is_text_accepts_non_empty_text(self):
        self.assertTrue(
            is_text("Cimento")
        )

    def test_is_text_rejects_empty_text(self):
        self.assertFalse(
            is_text("")
        )

    def test_is_text_rejects_none(self):
        self.assertFalse(
            is_text(None)
        )

    def test_is_numeric_accepts_decimal_value(self):
        self.assertTrue(
            is_numeric("123.4567")
        )

    def test_is_numeric_rejects_non_numeric_value(self):
        self.assertFalse(
            is_numeric("abc")
        )

    def test_is_numeric_or_dash_accepts_dash(self):
        self.assertTrue(
            is_numeric_or_dash("-")
        )

    def test_is_numeric_or_dash_accepts_numeric_value(self):
        self.assertTrue(
            is_numeric_or_dash("123.45")
        )

    def test_is_numeric_or_dash_rejects_invalid_value(self):
        self.assertFalse(
            is_numeric_or_dash("abc")
        )

    def test_matches_pattern_accepts_matching_code(self):
        self.assertTrue(
            matches_pattern(
                "M1001",
                r"M\d{4}",
            )
        )

    def test_matches_pattern_rejects_non_matching_code(self):
        self.assertFalse(
            matches_pattern(
                "M10001",
                r"M\d{4}",
            )
        )


class SyntheticDataRowDetectorTests(TestCase):

    def test_si_data_row_is_detected(self):
        row = pd.Series(
            [
                "1100001",
                "Composição",
                "m3",
                "123.4567",
            ]
        )

        self.assertTrue(
            is_si_data_row(row)
        )

    def test_si_data_row_requires_valid_code(self):
        row = pd.Series(
            [
                "110001",
                "Composição",
                "m3",
                "123.4567",
            ]
        )

        self.assertFalse(
            is_si_data_row(row)
        )

    def test_si_data_row_requires_numeric_value(self):
        row = pd.Series(
            [
                "1100001",
                "Composição",
                "m3",
                "abc",
            ]
        )

        self.assertFalse(
            is_si_data_row(row)
        )

    def test_material_data_row_is_detected(self):
        row = pd.Series(
            [
                "M1001",
                "Cimento",
                "kg",
                "12.3456",
            ]
        )

        self.assertTrue(
            is_material_data_row(row)
        )

    def test_material_data_row_accepts_dash_value(self):
        row = pd.Series(
            [
                "M1001",
                "Cimento",
                "kg",
                "-",
            ]
        )

        self.assertTrue(
            is_material_data_row(row)
        )

    def test_workman_data_row_is_detected(self):
        row = pd.Series(
            [
                "P9821",
                "Pedreiro",
                "h",
                "20.0",
                "0.0",
                "35.0",
                "0.0",
            ]
        )

        self.assertTrue(
            is_workman_data_row(row)
        )

    def test_workman_data_row_requires_seven_columns(self):
        row = pd.Series(
            [
                "P9821",
                "Pedreiro",
                "h",
                "20.0",
                "0.0",
                "35.0",
            ]
        )

        self.assertFalse(
            is_workman_data_row(row)
        )

    def test_equipment_data_row_with_e_code_is_detected(self):
        row = pd.Series(
            [
                "E1001",
                "Escavadeira",
                "100.0",
                "10.0",
                "5.0",
                "2.0",
                "3.0",
                "4.0",
                "5.0",
                "42.1930",
                "28.0238",
            ]
        )

        self.assertTrue(
            is_equipment_data_row(row)
        )

    def test_equipment_data_row_with_a_code_is_detected(self):
        row = pd.Series(
            [
                "A1001",
                "Caminhão",
                "100.0",
                "10.0",
                "5.0",
                "2.0",
                "3.0",
                "4.0",
                "5.0",
                "42.1930",
                "28.0238",
            ]
        )

        self.assertTrue(
            is_equipment_data_row(row)
        )

    def test_equipment_data_row_accepts_dash_values(self):
        row = pd.Series(
            [
                "E1001",
                "Escavadeira",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
            ]
        )

        self.assertTrue(
            is_equipment_data_row(row)
        )

    def test_equipment_data_row_requires_eleven_columns(self):
        row = pd.Series(
            [
                "E1001",
                "Escavadeira",
                "100.0",
                "10.0",
                "5.0",
                "2.0",
                "3.0",
                "4.0",
                "5.0",
                "42.1930",
            ]
        )

        self.assertFalse(
            is_equipment_data_row(row)
        )


class SyntheticFirstDataRowDetectionTests(TestCase):

    def test_first_si_data_row_is_detected(self):
        dataframe = pd.DataFrame(
            [
                ["Cabeçalho", None, None, None],
                ["Outro cabeçalho", None, None, None],
                [
                    "1100001",
                    "Composição",
                    "m3",
                    "123.4567",
                ],
            ]
        )

        result = detect_synthetic_structure(
            raw_dataframe=dataframe,
            type_file=SINTETICO,
        )

        self.assertEqual(
            result.first_data_row,
            2,
        )

    def test_first_material_data_row_is_detected(self):
        dataframe = pd.DataFrame(
            [
                ["Cabeçalho", None, None, None],
                [
                    "M1001",
                    "Cimento",
                    "kg",
                    "12.3456",
                ],
            ]
        )

        result = detect_synthetic_structure(
            raw_dataframe=dataframe,
            type_file=MATERIAL,
        )

        self.assertEqual(
            result.first_data_row,
            1,
        )

    def test_first_workman_data_row_is_detected(self):
        dataframe = pd.DataFrame(
            [
                ["Cabeçalho"] * 7,
                [
                    "P9821",
                    "Pedreiro",
                    "h",
                    "20.0",
                    "0.0",
                    "35.0",
                    "0.0",
                ],
            ]
        )

        result = detect_synthetic_structure(
            raw_dataframe=dataframe,
            type_file=MAODEOBRA,
        )

        self.assertEqual(
            result.first_data_row,
            1,
        )

    def test_first_equipment_data_row_is_detected(self):
        dataframe = pd.DataFrame(
            [
                ["Cabeçalho"] * 11,
                [
                    "E1001",
                    "Escavadeira",
                    "100.0",
                    "10.0",
                    "5.0",
                    "2.0",
                    "3.0",
                    "4.0",
                    "5.0",
                    "42.1930",
                    "28.0238",
                ],
            ]
        )

        result = detect_synthetic_structure(
            raw_dataframe=dataframe,
            type_file=EQUIPAMENTO,
        )

        self.assertEqual(
            result.first_data_row,
            1,
        )

    def test_headers_are_ignored_until_first_valid_row(self):
        dataframe = pd.DataFrame(
            [
                ["SISTEMA DE CUSTOS"],
                ["Código | Descrição | Unidade | Valor"],
                [
                    "M1001",
                    "Cimento",
                    "kg",
                    "12.3456",
                ],
            ]
        )

        result = detect_synthetic_structure(
            raw_dataframe=dataframe,
            type_file=MATERIAL,
        )

        self.assertEqual(
            result.first_data_row,
            2,
        )

    def test_missing_data_row_raises_value_error(self):
        dataframe = pd.DataFrame(
            [
                ["Cabeçalho", None, None, None],
                ["Ainda não é dado", None, None, None],
            ]
        )

        with self.assertRaises(ValueError):
            detect_synthetic_structure(
                raw_dataframe=dataframe,
                type_file=SINTETICO,
            )

    def test_unknown_file_type_raises_value_error(self):
        dataframe = pd.DataFrame(
            [
                [
                    "1100001",
                    "Composição",
                    "m3",
                    "123.4567",
                ]
            ]
        )

        with self.assertRaises(ValueError):
            detect_synthetic_structure(
                raw_dataframe=dataframe,
                type_file="INVALID",
            )