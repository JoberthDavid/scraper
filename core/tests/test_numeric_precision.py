from decimal import Decimal

import numpy as np
from django.test import SimpleTestCase


class NumericPrecisionTests(SimpleTestCase):
    def test_float64_has_lower_error_than_float32(self):
        value = 123456.7890123456
        decimal_reference = Decimal(str(value))

        float32_value = np.float32(value)
        float64_value = np.float64(value)

        float32_decimal = Decimal(str(float32_value))
        float64_decimal = Decimal(str(float64_value))

        error_float32 = abs(
            float32_decimal - decimal_reference
        )
        error_float64 = abs(
            float64_decimal - decimal_reference
        )

        self.assertGreater(
            error_float32,
            error_float64,
        )

    def test_float64_error_is_below_project_tolerance(self):
        value = 123456.7890123456
        decimal_reference = Decimal(str(value))

        float64_value = np.float64(value)
        float64_decimal = Decimal(str(float64_value))

        error_float64 = abs(
            float64_decimal - decimal_reference
        )

        self.assertLessEqual(
            error_float64,
            Decimal("0.000001"),
        )

    def test_float32_can_exceed_project_tolerance(self):
        value = 123456.7890123456
        decimal_reference = Decimal(str(value))

        float32_value = np.float32(value)
        float32_decimal = Decimal(str(float32_value))

        error_float32 = abs(
            float32_decimal - decimal_reference
        )

        self.assertGreater(
            error_float32,
            Decimal("0.000001"),
        )

    def test_decimal_preserves_decimal_text_exactly(self):
        text = "123456.7890123456"

        value = Decimal(text)

        self.assertEqual(
            value,
            Decimal("123456.7890123456"),
        )