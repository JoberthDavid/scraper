import pandas as pd
from django.test import SimpleTestCase

from core.usefuls.analytical_validator import (
    detect_analytical_compositions,
    count_analytical_composition_codes,
)


class AnalyticalDetectorTests(SimpleTestCase):
    def make_composition_row(
        self,
        code="1234567",
        description="Composição de teste",
    ):
        return [
            code,
            description,
            None,
            None,
            None,
            None,
            None,
            "Valores em reais (R$)",
            None,
        ]

    def test_detects_all_compositions_in_dataframe(self):
        data = pd.DataFrame(
            [
                ["Título", None, None, None, None, None, None, None, None],
                ["Cabeçalho", None, None, None, None, None, None, None, None],
                self.make_composition_row(
                    "1234567",
                    "Composição A",
                ),
                ["item", "entrada", 1, 2, 3, 4, 5, 6, 7],
                self.make_composition_row(
                    "7654321",
                    "Composição B",
                ),
            ]
        )

        compositions = detect_analytical_compositions(
            data
        )

        self.assertEqual(
            len(compositions),
            2,
        )

        self.assertEqual(
            compositions[0],
            {
                "row": 2,
                "code": "1234567",
                "description": "Composição A",
            },
        )

        self.assertEqual(
            compositions[1],
            {
                "row": 4,
                "code": "7654321",
                "description": "Composição B",
            },
        )

    def test_ignores_non_composition_rows(self):
        data = pd.DataFrame(
            [
                ["Título", None, None, None, None, None, None, None, None],
                ["1234567", "Descrição", 1, None, None, None, None, "Valores em reais (R$)", None],
                self.make_composition_row(
                    "1234567",
                    "Composição válida",
                ),
            ]
        )

        compositions = detect_analytical_compositions(
            data
        )

        self.assertEqual(
            len(compositions),
            1,
        )

        self.assertEqual(
            compositions[0]["row"],
            2,
        )

    def test_preserves_composition_order(self):
        data = pd.DataFrame(
            [
                self.make_composition_row(
                    "3000001",
                    "Primeira",
                ),
                self.make_composition_row(
                    "3000002",
                    "Segunda",
                ),
                self.make_composition_row(
                    "3000003",
                    "Terceira",
                ),
            ]
        )

        compositions = detect_analytical_compositions(
            data
        )

        self.assertEqual(
            [item["code"] for item in compositions],
            [
                "3000001",
                "3000002",
                "3000003",
            ],
        )

    def test_detects_duplicate_composition_codes(self):
        data = pd.DataFrame(
            [
                self.make_composition_row(
                    "3000001",
                    "Composição A",
                ),
                self.make_composition_row(
                    "3000001",
                    "Composição A - ocorrência 2",
                ),
                self.make_composition_row(
                    "3000002",
                    "Composição B",
                ),
            ]
        )

        compositions = detect_analytical_compositions(
            data
        )

        counts = count_analytical_composition_codes(
            compositions
        )

        self.assertEqual(
            counts["3000001"],
            2,
        )

        self.assertEqual(
            counts["3000002"],
            1,
        )

    def test_duplicate_code_does_not_remove_occurrence(self):
        data = pd.DataFrame(
            [
                self.make_composition_row(
                    "3000001",
                    "Composição A",
                ),
                self.make_composition_row(
                    "3000001",
                    "Composição A",
                ),
            ]
        )

        compositions = detect_analytical_compositions(
            data
        )

        self.assertEqual(
            len(compositions),
            2,
        )

        self.assertEqual(
            count_analytical_composition_codes(
                compositions
            )["3000001"],
            2,
        )

    def test_empty_dataframe_returns_no_compositions(self):
        data = pd.DataFrame()

        compositions = detect_analytical_compositions(
            data
        )

        self.assertEqual(
            compositions,
            [],
        )

    def test_detection_uses_original_dataframe_row_index(self):
        data = pd.DataFrame(
            [
                ["não é composição"] + [None] * 8,
                ["também não"] + [None] * 8,
                self.make_composition_row(
                    "9876543",
                    "Composição",
                ),
            ],
            index=[10, 20, 30],
        )

        compositions = detect_analytical_compositions(
            data
        )

        self.assertEqual(
            compositions[0]["row"],
            30,
        )