import pandas as pd

from django.test import SimpleTestCase

from core.usefuls.synthetic_integrity import (
    rows_are_identical,
)


class SyntheticDuplicateRowIntegrityTests(SimpleTestCase):

    def test_identical_duplicate_rows_are_considered_identical(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1001", "Cimento", "kg", 1.25],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

        self.assertTrue(
            rows_are_identical(dataframe)
        )

    def test_different_duplicate_rows_are_not_considered_identical(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", "kg", 1.25],
                ["M1001", "Cimento", "kg", 1.30],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

        self.assertFalse(
            rows_are_identical(dataframe)
        )

    def test_nan_values_in_same_column_are_considered_equal(self):
        dataframe = pd.DataFrame(
            [
                ["M1001", "Cimento", None, 1.25],
                ["M1001", "Cimento", None, 1.25],
            ],
            columns=[
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

        self.assertTrue(
            rows_are_identical(dataframe)
        )
