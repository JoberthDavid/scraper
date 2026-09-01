from decimal import Decimal


def decimal(value):
    return Decimal(str(value))

from core.models import (
    GenericItem,
    GenericDescription,
    MonetaryValue,
)

from core.usefuls.choices import (
    EQUIPAMENTO,
    PRODUTIVO,
    IMPRODUTIVO,
)


def rows_are_identical(group):
    """
    Returns True when all rows in a duplicated-code group
    contain exactly the same values.
    """

    first_row = group.iloc[0]

    for _, row in group.iloc[1:].iterrows():

        for column in group.columns:

            first_value = first_row[column]
            current_value = row[column]

            if current_value != first_value:

                if (
                    isinstance(current_value, float)
                    and isinstance(first_value, float)
                    and str(current_value) == "nan"
                    and str(first_value) == "nan"
                ):
                    continue

                return False

    return True


def audit_standard_synthetic_integrity(
    source_file,
    dataframe,
):
    """
    Audits SI / MA / MO style records.

    Returns a structured result describing inconsistencies between
    the expected DataFrame and the persisted database state.
    """

    from core.models import (
        GenericItem,
        GenericDescription,
        MonetaryValue,
    )

    expected = {}

    duplicate_codes = []
    inconsistent_duplicates = []

    for code, group in dataframe.groupby(
        "code",
        sort=False,
    ):
        if len(group) > 1:
            duplicate_codes.append(
                (code, len(group))
            )

            if not rows_are_identical(group):
                inconsistent_duplicates.append(
                    code
                )

        row = group.iloc[0]

        expected[code] = {
            "description": str(
                row["description"]
            ).strip(),
            "unit": str(
                row["unit"]
            ).strip(),
            "monetary_value": decimal(
                row["monetary_value"]
            ),
        }

    missing_items = []
    missing_descriptions = []
    missing_values = []

    wrong_descriptions = []
    wrong_values = []

    duplicate_items = []
    duplicate_descriptions = []
    duplicate_values = []

    for code, data in expected.items():

        items = GenericItem.objects.filter(
            code=code,
            source_files=source_file,
        )

        item_count = items.count()

        if item_count == 0:
            missing_items.append(code)
            continue

        if item_count > 1:
            duplicate_items.append(
                (code, item_count)
            )

        item = items.first()

        descriptions = GenericDescription.objects.filter(
            description=data["description"],
            source_files=source_file,
        )

        description_count = descriptions.count()

        if description_count == 0:
            missing_descriptions.append(code)

        elif description_count > 1:
            duplicate_descriptions.append(
                (code, description_count)
            )

        if not item.descriptions.filter(
            description=data["description"]
        ).exists():
            wrong_descriptions.append(
                (
                    code,
                    data["description"],
                )
            )

        values = MonetaryValue.objects.filter(
            generic_item=item,
            source_file=source_file,
        )

        value_count = values.count()

        if value_count == 0:
            missing_values.append(code)
            continue

        if value_count > 1:
            duplicate_values.append(
                (code, value_count)
            )

        database_value = decimal(
            values.first().monetary_value
        )

        if database_value != data["monetary_value"]:
            wrong_values.append(
                (
                    code,
                    data["monetary_value"],
                    database_value,
                )
            )

    passed = not any(
        [
            inconsistent_duplicates,
            missing_items,
            missing_descriptions,
            missing_values,
            wrong_descriptions,
            wrong_values,
            duplicate_items,
            duplicate_descriptions,
            duplicate_values,
        ]
    )

    return {
        "rows": len(dataframe),
        "entities": len(expected),
        "duplicate_codes": duplicate_codes,
        "inconsistent_duplicates": inconsistent_duplicates,
        "missing_items": missing_items,
        "missing_descriptions": missing_descriptions,
        "missing_values": missing_values,
        "wrong_descriptions": wrong_descriptions,
        "wrong_values": wrong_values,
        "duplicate_items": duplicate_items,
        "duplicate_descriptions": duplicate_descriptions,
        "duplicate_values": duplicate_values,
        "passed": passed,
    }


def audit_equipment_integrity(
    source_file,
    dataframe,
):
    """
    Audits equipment monetary structure.

    Each equipment must have exactly:

        one PRODUTIVO value
        one IMPRODUTIVO value
    """

    expected = {}

    duplicate_codes = []
    inconsistent_duplicates = []

    for code, group in dataframe.groupby(
        "code",
        sort=False,
    ):
        if len(group) > 1:
            duplicate_codes.append(
                (code, len(group))
            )

            if not rows_are_identical(group):
                inconsistent_duplicates.append(
                    code
                )

        row = group.iloc[0]

        expected[code] = {
            "description": str(
                row["description"]
            ).strip(),
            "unit": str(
                row["unit"]
            ).strip(),
            "productive_cost": decimal(
                row["productive_cost"]
            ),
            "unproductive_cost": decimal(
                row["unproductive_cost"]
            ),
        }

    missing_items = []
    missing_descriptions = []

    wrong_descriptions = []
    wrong_values = []
    wrong_monetary_structure = []

    duplicate_items = []
    duplicate_descriptions = []

    for code, data in expected.items():

        items = GenericItem.objects.filter(
            code=code,
            source_files=source_file,
        )

        item_count = items.count()

        if item_count == 0:
            missing_items.append(code)
            continue

        if item_count > 1:
            duplicate_items.append(
                (code, item_count)
            )

        item = items.first()

        descriptions = GenericDescription.objects.filter(
            description=data["description"],
            source_files=source_file,
        )

        description_count = descriptions.count()

        if description_count == 0:
            missing_descriptions.append(code)

        elif description_count > 1:
            duplicate_descriptions.append(
                (code, description_count)
            )

        if not item.descriptions.filter(
            description=data["description"]
        ).exists():
            wrong_descriptions.append(
                (
                    code,
                    data["description"],
                )
            )

        values = MonetaryValue.objects.filter(
            generic_item=item,
            source_file=source_file,
            group=EQUIPAMENTO,
        )

        value_count = values.count()

        if value_count != 2:
            wrong_monetary_structure.append(
                (
                    code,
                    value_count,
                )
            )
            continue

        productive = values.filter(
            classification=PRODUTIVO,
        )

        unproductive = values.filter(
            classification=IMPRODUTIVO,
        )

        if productive.count() != 1:
            wrong_monetary_structure.append(
                (
                    code,
                    PRODUTIVO,
                    productive.count(),
                )
            )
        else:
            database_value = decimal(
                productive.first().monetary_value
            )

            expected_value = data[
                "productive_cost"
            ]

            if database_value != expected_value:
                wrong_values.append(
                    (
                        code,
                        PRODUTIVO,
                        expected_value,
                        database_value,
                    )
                )

        if unproductive.count() != 1:
            wrong_monetary_structure.append(
                (
                    code,
                    IMPRODUTIVO,
                    unproductive.count(),
                )
            )
        else:
            database_value = decimal(
                unproductive.first().monetary_value
            )

            expected_value = data[
                "unproductive_cost"
            ]

            if database_value != expected_value:
                wrong_values.append(
                    (
                        code,
                        IMPRODUTIVO,
                        expected_value,
                        database_value,
                    )
                )

    passed = not any(
        [
            inconsistent_duplicates,
            missing_items,
            missing_descriptions,
            wrong_descriptions,
            wrong_values,
            wrong_monetary_structure,
            duplicate_items,
            duplicate_descriptions,
        ]
    )

    return {
        "rows": len(dataframe),
        "entities": len(expected),
        "duplicate_codes": duplicate_codes,
        "inconsistent_duplicates": inconsistent_duplicates,
        "missing_items": missing_items,
        "missing_descriptions": missing_descriptions,
        "wrong_descriptions": wrong_descriptions,
        "wrong_values": wrong_values,
        "wrong_monetary_structure": wrong_monetary_structure,
        "duplicate_items": duplicate_items,
        "duplicate_descriptions": duplicate_descriptions,
        "passed": passed,
    }
