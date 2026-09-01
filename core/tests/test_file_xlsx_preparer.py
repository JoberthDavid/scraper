from io import BytesIO
from unittest.mock import Mock

import pandas as pd
from django.test import SimpleTestCase

from core.usefuls.processing_file import FileXlsxPreparer


class FileXlsxPreparerTests(SimpleTestCase):
    def make_response(self, data_frame):
        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl",
        ) as writer:
            data_frame.to_excel(
                writer,
                index=False,
                header=False,
            )

        body = Mock()
        body.read.return_value = output.getvalue()

        return {
            "Body": body,
        }

    def test_prepare_sintetico_dataframe(self):
        data = pd.DataFrame(
            [
                ["Cabeçalho", None, None, None],
                ["Outro cabeçalho", None, None, None],
                [
                    "3009227",
                    "Serviço sintético",
                    "UN",
                    123.4567,
                ],
                [
                    "3009228",
                    "Outro serviço",
                    "M",
                    456.7891,
                ],
            ]
        )

        response = self.make_response(data)

        source_file = Mock()
        source_file.type_file = "SI"

        result = FileXlsxPreparer().get_data_frame_prepared(
            response=response,
            type_file="SI",
            source_file=source_file,
        )

        self.assertEqual(result.shape, (2, 4))

        self.assertEqual(
            list(result.columns),
            [
                "code",
                "description",
                "unit",
                "monetary_value",
            ],
        )

        self.assertEqual(
            result.iloc[0]["code"],
            "3009227",
        )

        self.assertEqual(
            result.iloc[-1]["code"],
            "3009228",
        )

    def test_prepare_sintetico_removes_header_rows(self):
        data = pd.DataFrame(
            [
                ["Título", None, None, None],
                ["Descrição", None, None, None],
                [
                    "3009227",
                    "Serviço",
                    "UN",
                    100.25,
                ],
            ]
        )

        response = self.make_response(data)

        source_file = Mock()
        source_file.type_file = "SI"

        result = FileXlsxPreparer().get_data_frame_prepared(
            response=response,
            type_file="SI",
            source_file=source_file,
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result.iloc[0]["code"],
            "3009227",
        )

    def test_prepare_sintetico_preserves_all_data_rows(self):
        data = pd.DataFrame(
            [
                ["Cabeçalho", None, None, None],
                [
                    "3009227",
                    "Serviço A",
                    "UN",
                    100.0,
                ],
                [
                    "3009228",
                    "Serviço B",
                    "M",
                    200.0,
                ],
                [
                    "3009229",
                    "Serviço C",
                    "KG",
                    300.0,
                ],
            ]
        )

        response = self.make_response(data)

        source_file = Mock()
        source_file.type_file = "SI"

        result = FileXlsxPreparer().get_data_frame_prepared(
            response=response,
            type_file="SI",
            source_file=source_file,
        )

        self.assertEqual(len(result), 3)

        self.assertEqual(
            result["code"].tolist(),
            [
                "3009227",
                "3009228",
                "3009229",
            ],
        )

    def test_prepare_sintetico_monetary_value_is_numeric(self):
        data = pd.DataFrame(
            [
                ["Cabeçalho", None, None, None],
                [
                    "3009227",
                    "Serviço",
                    "UN",
                    123.4567,
                ],
            ]
        )

        response = self.make_response(data)

        source_file = Mock()
        source_file.type_file = "SI"

        result = FileXlsxPreparer().get_data_frame_prepared(
            response=response,
            type_file="SI",
            source_file=source_file,
        )

        self.assertTrue(
            pd.api.types.is_numeric_dtype(
                result["monetary_value"]
            )
        )

        self.assertAlmostEqual(
            result.iloc[0]["monetary_value"],
            123.4567,
            places=7,
        )

    def test_prepare_equipment_adds_unit(self):
        data = pd.DataFrame(
            [
                ["Cabeçalho"] + [None] * 10,
                [
                    "E0001",
                    "Equipamento",
                    100.0,
                    10.0,
                    5.0,
                    2.0,
                    3.0,
                    4.0,
                    5.0,
                    120.0,
                    20.0,
                ],
            ]
        )

        response = self.make_response(data)

        source_file = Mock()
        source_file.type_file = "EQ"

        result = FileXlsxPreparer().get_data_frame_prepared(
            response=response,
            type_file="EQ",
            source_file=source_file,
        )

        self.assertIn(
            "unit",
            result.columns,
        )

        self.assertEqual(
            result.iloc[0]["unit"],
            "h",
        )


    def test_empty_response_is_rejected(self):
        body = Mock()
        body.read.return_value = b""

        response = {
            "Body": body,
        }

        source_file = Mock()
        source_file.type_file = "SI"

        with self.assertRaises(ValueError):
            FileXlsxPreparer().get_data_frame_prepared(
                response=response,
                type_file="SI",
                source_file=source_file,
            )