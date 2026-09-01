from io import BytesIO

import pandas as pd
from django.test import SimpleTestCase

from core.usefuls.si_validator import prepare_si_dataframe


class NumericSITests(SimpleTestCase):
    def make_xlsx(self):
        """
        Gera um XLSX artificial contendo valores monetários
        escolhidos explicitamente como referência.
        """
        rows = [
            ["Cabeçalho 1", None, None, None],
            ["Cabeçalho 2", None, None, None],
            [
                "1234567",
                "Serviço de teste A",
                "UN",
                12.3456789012,
            ],
            [
                "7654321",
                "Serviço de teste B",
                "M",
                9876.5432109876,
            ],
            [
                "2345678",
                "Serviço de teste C",
                "KG",
                0.1234567891,
            ],
            [
                "8765432",
                "Serviço de teste D",
                "M2",
                123456.7890123456,
            ],
        ]

        data_frame = pd.DataFrame(rows)

        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            data_frame.to_excel(
                writer,
                index=False,
                header=False,
            )

        return output.getvalue()

    def independent_reference(self, xlsx_content):
        """
        Leitura totalmente independente da função de preparação.

        Não utiliza:
        - prepare_si_dataframe()
        - find_first_data_row()
        - qualquer helper do si_validator.
        """
        raw = pd.read_excel(
            BytesIO(xlsx_content),
            header=None,
        )

        first_data_row = None

        for index, row in raw.iterrows():
            if len(row) < 4:
                continue

            code = row.iloc[0]
            description = row.iloc[1]
            unit = row.iloc[2]
            monetary = row.iloc[3]

            code_ok = (
                pd.notna(code)
                and str(code).strip().isdigit()
                and len(str(code).strip()) == 7
            )

            description_ok = (
                pd.notna(description)
                and str(description).strip() != ""
            )

            unit_ok = (
                pd.notna(unit)
                and str(unit).strip() != ""
            )

            monetary_ok = (
                pd.notna(monetary)
                and isinstance(monetary, (int, float))
            )

            if (
                code_ok
                and description_ok
                and unit_ok
                and monetary_ok
            ):
                first_data_row = index
                break

        if first_data_row is None:
            raise AssertionError(
                "A referência independente não encontrou "
                "a primeira linha de dados."
            )

        reference = (
            raw.iloc[first_data_row:, :4]
            .copy()
            .reset_index(drop=True)
        )

        reference.columns = [
            "code",
            "description",
            "unit",
            "monetary_value",
        ]

        reference["code"] = (
            reference["code"]
            .astype("string")
            .str.strip()
        )

        reference["description"] = (
            reference["description"]
            .astype("string")
            .str.strip()
        )

        reference["unit"] = (
            reference["unit"]
            .astype("string")
            .str.strip()
        )

        reference["monetary_value"] = pd.to_numeric(
            reference["monetary_value"],
            errors="raise",
        ).astype("float64")

        return reference, first_data_row

    def test_numeric_si_matches_independent_reference(self):
        """
        Compara o resultado oficial com uma leitura independente
        do mesmo XLSX.
        """
        xlsx_content = self.make_xlsx()

        expected, expected_first_row = (
            self.independent_reference(
                xlsx_content
            )
        )

        result = prepare_si_dataframe(
            xlsx_content
        )

        actual = result.data_frame

        self.assertEqual(
            result.first_data_row,
            expected_first_row,
        )

        self.assertEqual(
            actual.shape,
            expected.shape,
        )

        self.assertEqual(
            list(actual.columns),
            list(expected.columns),
        )

        self.assertEqual(
            actual["code"].tolist(),
            expected["code"].tolist(),
        )

        self.assertEqual(
            actual["description"].tolist(),
            expected["description"].tolist(),
        )

        self.assertEqual(
            actual["unit"].tolist(),
            expected["unit"].tolist(),
        )

        self.assertEqual(
            actual["monetary_value"].dtype,
            expected["monetary_value"].dtype,
        )

        pd.testing.assert_series_equal(
            actual["monetary_value"].reset_index(drop=True),
            expected["monetary_value"].reset_index(drop=True),
            check_exact=True,
            check_names=False,
        )

    def test_numeric_si_preserves_independent_source_values(self):
        """
        Compara os valores preparados contra os valores que foram
        explicitamente usados para construir o XLSX.
        """
        xlsx_content = self.make_xlsx()

        expected_values = [
            12.3456789012,
            9876.5432109876,
            0.1234567891,
            123456.7890123456,
        ]

        result = prepare_si_dataframe(
            xlsx_content
        )

        actual_values = (
            result.data_frame["monetary_value"]
            .tolist()
        )

        self.assertEqual(
            len(actual_values),
            len(expected_values),
        )

        for actual, expected in zip(
            actual_values,
            expected_values,
        ):
            self.assertAlmostEqual(
                actual,
                expected,
                places=12,
            )

    def test_independent_reference_reads_raw_monetary_values(self):
        """
        Garante que a referência independente realmente enxerga
        os valores monetários do XLSX antes da preparação oficial.
        """
        xlsx_content = self.make_xlsx()

        reference, _ = self.independent_reference(
            xlsx_content
        )

        expected = [
            12.3456789012,
            9876.5432109876,
            0.1234567891,
            123456.7890123456,
        ]

        self.assertEqual(
            len(reference),
            len(expected),
        )

        for actual, expected_value in zip(
            reference["monetary_value"],
            expected,
        ):
            self.assertAlmostEqual(
                actual,
                expected_value,
                places=12,
            )