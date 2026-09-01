from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

from core.usefuls.xlsx_validator import (
    find_first_data_row,
)

from io import BytesIO

from core.usefuls.choices import (
    SINTETICO,
    MATERIAL,
    MAODEOBRA,
    EQUIPAMENTO,
)

from core.usefuls.data_structure import (
    df_code,
    df_description,
    df_unit,
    df_monetary_value,
    df_wage,
    df_charges,
    df_unhealthy,
    df_purchase_value,
    df_deprecation,
    df_equity_opportunity,
    df_insurance_and_taxes,
    df_maintenance,
    df_operation,
    df_labor,
    df_productive_cost,
    df_unproductive_cost,
)


# ============================================================
# RESULTADO DA DETECÇÃO
# ============================================================

@dataclass(frozen=True)
class SyntheticDetectionResult:
    type_file: str
    first_data_row: int
    skiprows: int
    first_code: str
    first_description: str
    first_row: tuple[Any, ...]


@dataclass(frozen=True)
class SyntheticPreparationResult:
    data_frame: pd.DataFrame
    detection: SyntheticDetectionResult


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def is_text(value: Any) -> bool:
    if pd.isna(value):
        return False

    return bool(str(value).strip())


def is_numeric(value: Any) -> bool:
    if pd.isna(value):
        return False

    try:
        Decimal(str(value).strip())
        return True

    except (InvalidOperation, ValueError, TypeError):
        return False


def is_numeric_or_dash(value: Any) -> bool:
    if pd.isna(value):
        return False

    value = str(value).strip()

    if value == "-":
        return True

    return is_numeric(value)


def matches_pattern(
    value: Any,
    pattern: str,
) -> bool:

    if pd.isna(value):
        return False

    value = str(value).strip()

    return bool(
        re.fullmatch(
            pattern,
            value,
        )
    )


# ============================================================
# DETECTORES DE LINHA
# ============================================================

def is_si_data_row(row: pd.Series) -> bool:

    return (
        len(row) >= 4
        and matches_pattern(
            row.iloc[0],
            r"\d{7}",
        )
        and is_text(row.iloc[1])
        and is_text(row.iloc[2])
        and is_numeric(row.iloc[3])
    )


def is_material_data_row(row: pd.Series) -> bool:

    return (
        len(row) >= 4
        and matches_pattern(
            row.iloc[0],
            r"M\d{4}",
        )
        and is_text(row.iloc[1])
        and is_text(row.iloc[2])
        and is_numeric_or_dash(row.iloc[3])
    )


def is_workman_data_row(row: pd.Series) -> bool:

    return (
        len(row) >= 7
        and matches_pattern(
            row.iloc[0],
            r"P\d{4}",
        )
        and is_text(row.iloc[1])
        and is_text(row.iloc[2])
        and is_numeric_or_dash(row.iloc[3])
        and is_numeric_or_dash(row.iloc[4])
        and is_numeric_or_dash(row.iloc[5])
        and is_numeric_or_dash(row.iloc[6])
    )


def is_equipment_data_row(row: pd.Series) -> bool:

    return (
        len(row) >= 11
        and matches_pattern(
            row.iloc[0],
            r"[EA]\d{4}",
        )
        and is_text(row.iloc[1])
        and is_numeric_or_dash(row.iloc[2])
        and is_numeric_or_dash(row.iloc[3])
        and is_numeric_or_dash(row.iloc[4])
        and is_numeric_or_dash(row.iloc[5])
        and is_numeric_or_dash(row.iloc[6])
        and is_numeric_or_dash(row.iloc[7])
        and is_numeric_or_dash(row.iloc[8])
        and is_numeric_or_dash(row.iloc[9])
        and is_numeric_or_dash(row.iloc[10])
    )


ROW_VALIDATORS = {
    SINTETICO: is_si_data_row,
    MATERIAL: is_material_data_row,
    MAODEOBRA: is_workman_data_row,
    EQUIPAMENTO: is_equipment_data_row,
}


# ============================================================
# CONFIGURAÇÃO DOS DATAFRAMES
# ============================================================

COLUMNS_BY_TYPE = {
    SINTETICO: [
        df_code,
        df_description,
        df_unit,
        df_monetary_value,
    ],

    MATERIAL: [
        df_code,
        df_description,
        df_unit,
        df_monetary_value,
    ],

    MAODEOBRA: [
        df_code,
        df_description,
        df_unit,
        df_wage,
        df_charges,
        df_monetary_value,
        df_unhealthy,
    ],

    EQUIPAMENTO: [
        df_code,
        df_description,
        df_purchase_value,
        df_deprecation,
        df_equity_opportunity,
        df_insurance_and_taxes,
        df_maintenance,
        df_operation,
        df_labor,
        df_productive_cost,
        df_unproductive_cost,
        "unit",
    ],
}


NUMERIC_COLUMNS_BY_TYPE = {
    SINTETICO: [
        df_monetary_value,
    ],

    MATERIAL: [
        df_monetary_value,
    ],

    MAODEOBRA: [
        df_wage,
        df_charges,
        df_monetary_value,
        df_unhealthy,
    ],

    EQUIPAMENTO: [
        df_purchase_value,
        df_deprecation,
        df_equity_opportunity,
        df_insurance_and_taxes,
        df_maintenance,
        df_operation,
        df_labor,
        df_productive_cost,
        df_unproductive_cost,
    ],
}


TEXT_COLUMNS_BY_TYPE = {
    SINTETICO: [
        df_code,
        df_description,
        df_unit,
    ],

    MATERIAL: [
        df_code,
        df_description,
        df_unit,
    ],

    MAODEOBRA: [
        df_code,
        df_description,
        df_unit,
    ],

    EQUIPAMENTO: [
        df_code,
        df_description,
    ],
}


# ============================================================
# DETECÇÃO
# ============================================================

def detect_synthetic_structure(
    raw_dataframe: pd.DataFrame,
    type_file: str,
) -> SyntheticDetectionResult:

    try:
        row_validator = ROW_VALIDATORS[type_file]
    except KeyError as exc:
        raise ValueError(
            f"Tipo de arquivo não suportado: {type_file}"
        ) from exc

    first_data_row = find_first_data_row(
        raw_dataframe=raw_dataframe,
        row_validator=row_validator,
    )

    row = raw_dataframe.iloc[first_data_row]

    return SyntheticDetectionResult(
        type_file=type_file,
        first_data_row=first_data_row,
        skiprows=max(first_data_row - 1, 0),
        first_code=str(row.iloc[0]).strip(),
        first_description=str(row.iloc[1]).strip(),
        first_row=tuple(row.tolist()),
    )


# ============================================================
# PREPARAÇÃO
# ============================================================

def prepare_synthetic_dataframe(
    xlsx_content: bytes,
    type_file: str,
) -> SyntheticPreparationResult:

    if not xlsx_content:
        raise ValueError(
            "O conteúdo do XLSX está vazio."
        )

    if type_file not in COLUMNS_BY_TYPE:
        raise ValueError(
            f"Tipo de arquivo não suportado: {type_file}"
        )

    # --------------------------------------------------------
    # Uma única leitura
    # --------------------------------------------------------

    raw_dataframe = pd.read_excel(
        BytesIO(xlsx_content),
        header=None,
    )
    # --------------------------------------------------------
    # Detectar primeira linha
    # --------------------------------------------------------

    detection = detect_synthetic_structure(
        raw_dataframe=raw_dataframe,
        type_file=type_file,
    )

    # --------------------------------------------------------
    # Recortar dados
    # --------------------------------------------------------

    data_frame = (
        raw_dataframe
        .iloc[detection.first_data_row:]
        .copy()
        .reset_index(drop=True)
    )

    columns = COLUMNS_BY_TYPE[type_file]

    # --------------------------------------------------------
    # Colunas que realmente vêm do Excel
    # --------------------------------------------------------

    if type_file == EQUIPAMENTO:
        source_columns = columns[:-1]
    else:
        source_columns = columns

    if data_frame.shape[1] < len(source_columns):
        raise ValueError(
            f"O arquivo possui {data_frame.shape[1]} colunas, "
            f"mas são necessárias {len(source_columns)}."
        )

    data_frame = data_frame.iloc[
        :,
        :len(source_columns),
    ].copy()

    data_frame.columns = source_columns

    # --------------------------------------------------------
    # Equipamentos:
    # 'unit' não existe no XLSX; é criada pelo processamento
    # original e assume sempre 'h'.
    # --------------------------------------------------------

    if type_file == EQUIPAMENTO:
        data_frame["unit"] = "h"

    # --------------------------------------------------------
    # Texto
    # --------------------------------------------------------

    for column in TEXT_COLUMNS_BY_TYPE[type_file]:

        data_frame[column] = (
            data_frame[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # Valores numéricos
    # --------------------------------------------------------

    for column in NUMERIC_COLUMNS_BY_TYPE[type_file]:

        data_frame[column] = (
            data_frame[column]
            .replace("-", 0)
        )

        data_frame[column] = pd.to_numeric(
            data_frame[column],
            errors="raise",
        ).astype("float64")

    if data_frame.shape[1] < len(columns):
        raise ValueError(
            f"O arquivo possui {data_frame.shape[1]} colunas, "
            f"mas são necessárias {len(columns)}."
        )

    data_frame = data_frame.iloc[
        :,
        :len(columns),
    ].copy()

    data_frame.columns = columns

    # --------------------------------------------------------
    # Texto
    # --------------------------------------------------------

    for column in TEXT_COLUMNS_BY_TYPE[type_file]:

        data_frame[column] = (
            data_frame[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # Numéricos
    # --------------------------------------------------------

    for column in NUMERIC_COLUMNS_BY_TYPE[type_file]:

        data_frame[column] = (
            data_frame[column]
            .replace("-", 0)
        )

        data_frame[column] = pd.to_numeric(
            data_frame[column],
            errors="raise",
        ).astype("float64")

    # --------------------------------------------------------
    # Equipamentos
    # --------------------------------------------------------

    if type_file == EQUIPAMENTO:
        data_frame["unit"] = "h"

    return SyntheticPreparationResult(
        data_frame=data_frame,
        detection=detection,
    )