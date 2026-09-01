
from __future__ import annotations

from collections import Counter
import re

import pandas as pd

from core.usefuls.xlsx_validator import (
    find_first_data_row,
)


COMPOSITION_CODE_PATTERN = re.compile(
    r"\d{7}"
)

COMPOSITION_VALUE_LABEL = (
    "Valores em reais (R$)"
)


def is_analytical_composition_header(
    row: pd.Series,
) -> bool:
    """
    Identifica uma linha inicial de composição do
    arquivo ANALÍTICO.

    Estrutura esperada:

        A = código numérico de 7 dígitos
        B = descrição não vazia
        C:G = vazias
        H = "Valores em reais (R$)"
        I = vazia
    """

    if len(row) < 9:
        return False

    code = row.iloc[0]

    if pd.isna(code):
        return False

    code = str(code).strip()

    if not COMPOSITION_CODE_PATTERN.fullmatch(code):
        return False

    description = row.iloc[1]

    if pd.isna(description):
        return False

    description = str(description).strip()

    if not description:
        return False

    for position in range(2, 7):
        if not pd.isna(row.iloc[position]):
            return False

    value_label = row.iloc[7]

    if (
        pd.isna(value_label)
        or str(value_label).strip()
        != COMPOSITION_VALUE_LABEL
    ):
        return False

    if not pd.isna(row.iloc[8]):
        return False

    return True


def find_first_analytical_composition_row(
    raw_dataframe: pd.DataFrame,
) -> int:
    """
    Localiza a primeira linha de composição de um
    DataFrame ANALÍTICO bruto.
    """

    return find_first_data_row(
        raw_dataframe=raw_dataframe,
        row_validator=is_analytical_composition_header,
    )

def composition_has_inputs(composition):
    """
    Returns True when the composition has at least one input
    of any supported type.
    """

    return any(
        [
            composition.equipments.exists(),
            composition.workmen.exists(),
            composition.materials.exists(),
            composition.activities.exists(),
            composition.transports.exists(),
        ]
    )


def is_analytical_composition_header(
    row: pd.Series,
) -> bool:
    """
    Identifica a linha inicial de uma composição do AN.

    Regras:
        A = código numérico de 7 dígitos
        B = descrição não vazia
        C:G = vazias
        H = "Valores em reais (R$)"
        I = vazia
    """
    if len(row) < 9:
        return False

    code = row.iloc[0]
    description = row.iloc[1]

    if pd.isna(code):
        return False

    code = str(code).strip()

    if not re.fullmatch(r"\d{7}", code):
        return False

    if pd.isna(description):
        return False

    description = str(description).strip()

    if not description:
        return False

    for position in range(2, 7):
        if not pd.isna(row.iloc[position]):
            return False

    value_label = row.iloc[7]

    if (
        pd.isna(value_label)
        or str(value_label).strip()
        != "Valores em reais (R$)"
    ):
        return False

    if not pd.isna(row.iloc[8]):
        return False

    return True


def detect_analytical_compositions(
    data_frame: pd.DataFrame,
) -> list[dict]:
    """
    Percorre o DataFrame bruto e retorna todas as composições AN
    detectadas.
    """
    compositions = []

    for index, row in data_frame.iterrows():
        if not is_analytical_composition_header(row):
            continue

        compositions.append(
            {
                "row": int(index),
                "code": str(row.iloc[0]).strip(),
                "description": str(row.iloc[1]).strip(),
            }
        )

    return compositions


def count_analytical_composition_codes(
    compositions: list[dict],
) -> Counter:
    """
    Retorna a contagem de ocorrências de cada código de composição.
    """
    return Counter(
        item["code"]
        for item in compositions
    )