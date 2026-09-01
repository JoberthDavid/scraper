from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

from core.usefuls.xlsx_validator import (
    prepare_dataframe_from_xlsx,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

SI_COLUMNS = (
    "code",
    "description",
    "unit",
    "monetary_value",
)


# ============================================================
# RESULTADOS
# ============================================================

@dataclass(frozen=True)
class SIValidationResult:

    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    stats: dict[str, Any]


@dataclass(frozen=True)
class SIPreparationResult:

    data_frame: pd.DataFrame
    first_data_row: int
    validation: SIValidationResult


# ============================================================
# REGRAS DE IDENTIFICAÇÃO
# ============================================================

def _is_valid_code(value: Any) -> bool:

    if pd.isna(value):
        return False

    value = str(value).strip()

    return (
        value.isdigit()
        and len(value) == 7
    )


def _is_valid_text(value: Any) -> bool:

    if pd.isna(value):
        return False

    return bool(str(value).strip())


def _is_valid_monetary_value(value: Any) -> bool:

    if pd.isna(value):
        return False

    try:
        Decimal(str(value).strip())
        return True

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return False


def is_si_data_row(
    row: pd.Series,
) -> bool:

    if len(row) < 4:
        return False

    return (
        _is_valid_code(row.iloc[0])
        and _is_valid_text(row.iloc[1])
        and _is_valid_text(row.iloc[2])
        and _is_valid_monetary_value(row.iloc[3])
    )


# ============================================================
# PREPARAÇÃO
# ============================================================

def prepare_si_dataframe(
    xlsx_content: bytes,
) -> SIPreparationResult:

    data_frame, first_data_row = (
        prepare_dataframe_from_xlsx(
            xlsx_content=xlsx_content,
            row_validator=is_si_data_row,
            columns=SI_COLUMNS,
            numeric_columns=("monetary_value",),
        )
    )

    # --------------------------------------------------------
    # Tipagem textual
    # --------------------------------------------------------

    data_frame["code"] = (
        data_frame["code"]
        .astype("string")
        .str.strip()
    )

    data_frame["description"] = (
        data_frame["description"]
        .astype("string")
        .str.strip()
    )

    data_frame["unit"] = (
        data_frame["unit"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # IMPORTANTE:
    # float64, e não float32.
    # --------------------------------------------------------

    data_frame["monetary_value"] = (
        data_frame["monetary_value"]
        .astype("float64")
    )

    validation = validate_si_dataframe(
        data_frame
    )

    return SIPreparationResult(
        data_frame=data_frame,
        first_data_row=first_data_row,
        validation=validation,
    )


# ============================================================
# VALIDAÇÃO
# ============================================================

def validate_si_dataframe(
    data_frame: pd.DataFrame,
) -> SIValidationResult:

    errors: list[str] = []
    warnings: list[str] = []

    if data_frame.empty:

        return SIValidationResult(
            valid=False,
            errors=("DataFrame SI vazio.",),
            warnings=(),
            stats={},
        )

    if len(data_frame.columns) != 4:

        errors.append(
            "Quantidade de colunas inválida: "
            f"esperado=4, "
            f"recebido={len(data_frame.columns)}"
        )

    code_column = data_frame.iloc[:, 0]
    description_column = data_frame.iloc[:, 1]
    unit_column = data_frame.iloc[:, 2]
    monetary_column = data_frame.iloc[:, 3]

    codes = (
        code_column
        .astype("string")
        .str.strip()
    )

    invalid_code_mask = ~codes.str.fullmatch(
        r"\d{7}",
        na=False,
    )

    invalid_code_count = int(
        invalid_code_mask.sum()
    )

    if invalid_code_count:

        examples = (
            codes[invalid_code_mask]
            .drop_duplicates()
            .head(10)
            .tolist()
        )

        errors.append(
            f"{invalid_code_count} código(s) inválido(s). "
            f"Exemplos: {examples}"
        )

    descriptions = (
        description_column
        .astype("string")
        .str.strip()
    )

    empty_description_count = int(
        (
            descriptions.isna()
            | descriptions.eq("")
        ).sum()
    )

    if empty_description_count:

        errors.append(
            f"{empty_description_count} "
            "descrição(ões) vazia(s)."
        )

    units = (
        unit_column
        .astype("string")
        .str.strip()
    )

    empty_unit_count = int(
        (
            units.isna()
            | units.eq("")
        ).sum()
    )

    if empty_unit_count:

        errors.append(
            f"{empty_unit_count} unidade(s) vazia(s)."
        )

    monetary_numeric = pd.to_numeric(
        monetary_column,
        errors="coerce",
    )

    invalid_monetary_count = int(
        monetary_numeric.isna().sum()
    )

    if invalid_monetary_count:

        examples = (
            monetary_column[
                monetary_numeric.isna()
            ]
            .drop_duplicates()
            .head(10)
            .astype(str)
            .tolist()
        )

        errors.append(
            f"{invalid_monetary_count} valor(es) "
            "monetário(s) inválido(s). "
            f"Exemplos: {examples}"
        )

    duplicated_codes = (
        codes[
            codes.duplicated(
                keep=False
            )
        ]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    if duplicated_codes:

        warnings.append(
            "Existem códigos duplicados no DataFrame. "
            f"Quantidade: {len(duplicated_codes)}."
        )

    stats = {
        "rows": len(data_frame),
        "columns": len(data_frame.columns),
        "distinct_codes": int(
            codes.nunique()
        ),
        "first_code": str(
            codes.iloc[0]
        ),
        "last_code": str(
            codes.iloc[-1]
        ),
        "invalid_code_count": (
            invalid_code_count
        ),
        "empty_description_count": (
            empty_description_count
        ),
        "empty_unit_count": (
            empty_unit_count
        ),
        "invalid_monetary_count": (
            invalid_monetary_count
        ),
    }

    return SIValidationResult(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        stats=stats,
    )