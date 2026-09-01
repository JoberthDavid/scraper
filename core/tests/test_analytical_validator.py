from unittest import TestCase

import pandas as pd


from core.usefuls.analytical_validator import (
    is_analytical_composition_header,
    find_first_analytical_composition_row,
    composition_has_inputs,
)

class AnalyticalCompositionHeaderTests(TestCase):

    def valid_row(self):
        return pd.Series([
            "1100001",
            "Execução de concreto",
            None,
            None,
            None,
            None,
            None,
            "Valores em reais (R$)",
            None,
        ])

    def test_valid_composition_header_is_accepted(self):
        self.assertTrue(
            is_analytical_composition_header(
                self.valid_row()
            )
        )

    def test_code_must_have_seven_digits(self):
        row = self.valid_row()
        row.iloc[0] = "110001"

        self.assertFalse(
            is_analytical_composition_header(row)
        )

    def test_description_must_not_be_empty(self):
        row = self.valid_row()
        row.iloc[1] = ""

        self.assertFalse(
            is_analytical_composition_header(row)
        )

    def test_columns_c_to_g_must_be_empty(self):
        row = self.valid_row()
        row.iloc[2] = 1

        self.assertFalse(
            is_analytical_composition_header(row)
        )

    def test_value_label_must_be_present_in_column_h(self):
        row = self.valid_row()
        row.iloc[7] = "Outro valor"

        self.assertFalse(
            is_analytical_composition_header(row)
        )

    def test_column_i_must_be_empty(self):
        row = self.valid_row()
        row.iloc[8] = "m3"

        self.assertFalse(
            is_analytical_composition_header(row)
        )

    def test_row_with_less_than_nine_columns_is_rejected(self):
        row = pd.Series([
            "1100001",
            "Execução de concreto",
            None,
            None,
            None,
            None,
            None,
            "Valores em reais (R$)",
        ])

        self.assertFalse(
            is_analytical_composition_header(row)
        )

    def test_null_code_is_rejected(self):
        row = self.valid_row()
        row.iloc[0] = None

        self.assertFalse(
            is_analytical_composition_header(row)
        )


class AnalyticalCompositionRowDetectionTests(TestCase):

    def test_first_composition_row_is_detected(self):
        dataframe = pd.DataFrame([
            ["Cabeçalho", None, None, None],
            ["Outro cabeçalho", None, None, None],
            [
                "1100001",
                "Execução de concreto",
                None,
                None,
                None,
                None,
                None,
                "Valores em reais (R$)",
                None,
            ],
        ])

        self.assertEqual(
            find_first_analytical_composition_row(
                dataframe
            ),
            2,
        )

    def test_headers_are_ignored_until_first_valid_composition(self):
        dataframe = pd.DataFrame([
            ["SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS"],
            ["Custo Unitário de Referência"],
            [
                "1100001",
                "Execução de concreto",
                None,
                None,
                None,
                None,
                None,
                "Valores em reais (R$)",
                None,
            ],
        ])

        self.assertEqual(
            find_first_analytical_composition_row(
                dataframe
            ),
            2,
        )

    def test_missing_composition_raises_value_error(self):
        dataframe = pd.DataFrame([
            ["Cabeçalho"],
            ["Ainda não é uma composição"],
        ])

        with self.assertRaises(ValueError):
            find_first_analytical_composition_row(
                dataframe
            )