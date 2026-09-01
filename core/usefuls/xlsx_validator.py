from __future__ import annotations

from collections.abc import Callable, Sequence
from io import BytesIO
from typing import Any

import pandas as pd


RowValidator = Callable[[pd.Series], bool]


def find_first_data_row(
    raw_dataframe: pd.DataFrame,
    row_validator: RowValidator,
) -> int:
    """
    Localiza a primeira linha real de dados de um XLSX.

    O DataFrame deve ter sido lido com header=None.

    A função não conhece o formato do arquivo. A definição do que
    constitui uma linha válida é fornecida por row_validator.
    """

    if raw_dataframe.empty:
        raise ValueError(
            "O DataFrame bruto está vazio."
        )

    for index, row in raw_dataframe.iterrows():
        if row_validator(row):
            return int(index)

    raise ValueError(
        "Não foi possível localizar a primeira linha "
        "de dados do arquivo."
    )


def prepare_dataframe_from_xlsx(
    xlsx_content: bytes,
    *,
    row_validator: RowValidator,
    columns: Sequence[str],
    converters: dict[int, Callable[[Any], Any]] | None = None,
    numeric_columns: Sequence[str] = (),
) -> tuple[pd.DataFrame, int]:
    """
    Lê um XLSX uma única vez, detecta a primeira linha de dados,
    recorta o DataFrame e aplica a tipagem final.

    Retorna:
        (data_frame, first_data_row)
    """

    if not xlsx_content:
        raise ValueError(
            "O conteúdo do XLSX está vazio."
        )

    raw_dataframe = pd.read_excel(
        BytesIO(xlsx_content),
        header=None,
    )

    first_data_row = find_first_data_row(
        raw_dataframe=raw_dataframe,
        row_validator=row_validator,
    )

    data_frame = (
        raw_dataframe
        .iloc[first_data_row:]
        .copy()
        .reset_index(drop=True)
    )

    if len(columns) > data_frame.shape[1]:
        raise ValueError(
            f"O arquivo possui {data_frame.shape[1]} colunas, "
            f"mas são necessárias {len(columns)}."
        )

    data_frame = data_frame.iloc[
        :,
        :len(columns),
    ].copy()

    data_frame.columns = list(columns)

    # ---------------------------------------------------------
    # Converters
    # ---------------------------------------------------------

    if converters:
        for column_index, converter in converters.items():
            column = data_frame.columns[column_index]

            data_frame[column] = (
                data_frame[column]
                .map(converter)
            )

    # ---------------------------------------------------------
    # Colunas numéricas
    # ---------------------------------------------------------

    for column in numeric_columns:
        data_frame[column] = pd.to_numeric(
            data_frame[column],
            errors="raise",
        )

    return data_frame, first_data_row
