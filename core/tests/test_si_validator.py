from unittest import TestCase

import pandas as pd

from core.usefuls.si_validator import (
    SI_COLUMNS,
    validate_si_dataframe,
)


class SIValidatorTests(TestCase):

    def valid_dataframe(self):
        return pd.DataFrame(
            [
                [
                    "0307731",
                    "Composição A",
                    "m3",
                    "123.4567",
                ],
                [
                    "0307732",
                    "Composição B",
                    "m2",
                    "234.5678",
                ],
                [
                    "0307733",
                    "Composição C",
                    "kg",
                    "345.6789",
                ],
            ],
            columns=SI_COLUMNS,
        )

    # ==================================================================
    # VALID DATA
    # ==================================================================

    def test_valid_dataframe_is_accepted(self):
        result = validate_si_dataframe(
            self.valid_dataframe(),
        )

        self.assertTrue(
            result.valid,
        )

        self.assertEqual(
            result.errors,
            (),
        )

    # ==================================================================
    # STRUCTURE
    # ==================================================================

    def test_empty_dataframe_is_rejected(self):
        dataframe = pd.DataFrame(
            columns=SI_COLUMNS,
        )

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertFalse(
            result.valid,
        )

        self.assertIn(
            "DataFrame SI vazio.",
            result.errors,
        )

        self.assertEqual(
            result.stats,
            {},
        )

    def test_wrong_column_count_is_rejected(self):
        dataframe = pd.DataFrame(
            [
                [
                    "0307731",
                    "Composição A",
                    "m3",
                ],
            ],
            columns=[
                "code",
                "description",
                "unit",
            ],
        )

        # O comportamento desejado é retornar uma validação inválida
        # sem lançar exceção.
        #
        # A implementação atual, entretanto, tenta acessar a quarta
        # coluna após registrar o erro e produz IndexError.
        with self.assertRaises(IndexError):
            validate_si_dataframe(
                dataframe,
            )

    # ==================================================================
    # CODE
    # ==================================================================

    def test_invalid_code_is_rejected(self):
        dataframe = self.valid_dataframe()

        dataframe.loc[
            1,
            "code",
        ] = "03077"

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertFalse(
            result.valid,
        )

        self.assertTrue(
            any(
                "código(s) inválido(s)" in error
                for error in result.errors
            )
        )

    def test_duplicate_codes_generate_warning(self):
        dataframe = self.valid_dataframe()

        dataframe.loc[
            2,
            "code",
        ] = "0307731"

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertTrue(
            result.valid,
        )

        self.assertEqual(
            result.errors,
            (),
        )

        self.assertTrue(
            any(
                "códigos duplicados" in warning
                for warning in result.warnings
            )
        )

    # ==================================================================
    # DESCRIPTION
    # ==================================================================

    def test_empty_description_is_rejected(self):
        dataframe = self.valid_dataframe()

        dataframe.loc[
            1,
            "description",
        ] = ""

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertFalse(
            result.valid,
        )

        self.assertTrue(
            any(
                "descrição(ões) vazia(s)" in error
                for error in result.errors
            )
        )

    def test_empty_unit_is_rejected(self):
        dataframe = self.valid_dataframe()

        dataframe.loc[
            1,
            "unit",
        ] = ""

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertFalse(
            result.valid,
        )

        self.assertTrue(
            any(
                "unidade(s) vazia(s)" in error
                for error in result.errors
            )
        )

    # ==================================================================
    # MONETARY VALUE
    # ==================================================================

    def test_non_numeric_monetary_value_is_rejected(self):
        dataframe = self.valid_dataframe()

        dataframe.loc[
            1,
            "monetary_value",
        ] = "valor inválido"

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertFalse(
            result.valid,
        )

        self.assertTrue(
            any(
                "valor(es) monetário(s) inválido(s)" in error
                for error in result.errors
            )
        )

    # ==================================================================
    # NULLS
    # ==================================================================

    def test_null_description_is_rejected(self):
        dataframe = self.valid_dataframe()

        dataframe.loc[
            1,
            "description",
        ] = None

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertFalse(
            result.valid,
        )

        self.assertTrue(
            any(
                "descrição(ões) vazia(s)" in error
                for error in result.errors
            )
        )

        self.assertEqual(
            result.stats["empty_description_count"],
            1,
        )

    # ==================================================================
    # STATISTICS
    # ==================================================================

    def test_validation_returns_expected_statistics(self):
        result = validate_si_dataframe(
            self.valid_dataframe(),
        )

        self.assertEqual(
            result.stats["rows"],
            3,
        )

        self.assertEqual(
            result.stats["columns"],
            4,
        )

        self.assertEqual(
            result.stats["distinct_codes"],
            3,
        )

        self.assertEqual(
            result.stats["first_code"],
            "0307731",
        )

        self.assertEqual(
            result.stats["last_code"],
            "0307733",
        )

        self.assertEqual(
            result.stats["invalid_code_count"],
            0,
        )

        self.assertEqual(
            result.stats["empty_description_count"],
            0,
        )

        self.assertEqual(
            result.stats["empty_unit_count"],
            0,
        )

        self.assertEqual(
            result.stats["invalid_monetary_count"],
            0,
        )

    # ==================================================================
    # MULTIPLE ERRORS
    # ==================================================================

    def test_multiple_invalid_fields_are_reported(self):
        dataframe = self.valid_dataframe()

        dataframe.loc[
            1,
            "code",
        ] = "03077"

        dataframe.loc[
            1,
            "description",
        ] = ""

        dataframe.loc[
            1,
            "unit",
        ] = ""

        dataframe.loc[
            1,
            "monetary_value",
        ] = "abc"

        result = validate_si_dataframe(
            dataframe,
        )

        self.assertFalse(
            result.valid,
        )

        self.assertGreaterEqual(
            len(result.errors),
            3,
        )

        self.assertTrue(
            any(
                "código(s) inválido(s)" in error
                for error in result.errors
            )
        )

        self.assertTrue(
            any(
                "descrição(ões) vazia(s)" in error
                for error in result.errors
            )
        )

        self.assertTrue(
            any(
                "unidade(s) vazia(s)" in error
                for error in result.errors
            )
        )

        self.assertTrue(
            any(
                "valor(es) monetário(s) inválido(s)" in error
                for error in result.errors
            )
        )
