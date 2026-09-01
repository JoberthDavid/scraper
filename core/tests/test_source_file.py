from datetime import date

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from core.models import SourceFile

from core.usefuls.choices import (
    SICRO,
    GOIAS,
    DISTRITO_FEDERAL,
    ONERADO,
    ANALITICO,
)


def create_source_file(
    *,
    data_base=date(2023, 7, 1),
    source_file="teste.xlsx",
    methodology=SICRO,
    uf=GOIAS,
    type_system=ONERADO,
    type_file=ANALITICO,
    status=False,
    number_of_lines_to_skip=0,
):
    """
    Create the minimum SourceFile required by the tests.

    The FileField receives a simple filename so these tests do not
    depend on an external storage service.
    """

    return SourceFile.objects.create(
        data_base=data_base,
        source_file=source_file,
        methodology=methodology,
        uf=uf,
        type_system=type_system,
        type_file=type_file,
        status=status,
        number_of_lines_to_skip=number_of_lines_to_skip,
    )


class SourceFileTests(TestCase):
    """
    Tests for SourceFile persistence, validation, defaults and
    database constraints.
    """

    def test_create_source_file(self):
        source_file = create_source_file()

        self.assertIsNotNone(
            source_file.pk,
        )

        self.assertEqual(
            source_file.methodology,
            SICRO,
        )

        self.assertEqual(
            source_file.uf,
            GOIAS,
        )

    def test_save_source_file(self):
        source_file = create_source_file()

        source_file.save()

        source_file.refresh_from_db()

        self.assertEqual(
            source_file.source_file.name,
            "teste.xlsx",
        )

    def test_retrieve_source_file_content(self):
        source_file = create_source_file(
            source_file="teste.xlsx",
        )

        content = b"test content"

        source_file.source_file.save(
            "teste.xlsx",
            ContentFile(content),
            save=True,
        )

        source_file.refresh_from_db()

        with source_file.source_file.open("rb") as file:
            self.assertEqual(
                file.read(),
                content,
            )

    def test_xlsx_extension_is_valid(self):
        source_file = create_source_file(
            source_file="teste.xlsx",
        )

        source_file.full_clean()

        self.assertEqual(
            source_file.source_file.name,
            "teste.xlsx",
        )

    def test_invalid_file_extension_is_rejected(self):
        source_file = create_source_file(
            source_file="teste.pdf",
        )

        with self.assertRaises(ValidationError):
            source_file.full_clean()

    def test_default_values_are_applied(self):
        source_file = create_source_file()

        self.assertFalse(
            source_file.status,
        )

        self.assertEqual(
            source_file.number_of_lines_to_skip,
            0,
        )

    def test_duplicate_unique_combination_is_rejected(self):
        create_source_file()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_source_file()


    def test_empty_date_base_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_source_file(
                    data_base=None,
                )


    def test_empty_file_type_is_rejected(self):
        source_file = create_source_file(
            type_file="",
        )

        with self.assertRaises(ValidationError):
            source_file.full_clean()

    def test_empty_source_file_is_rejected(self):
        source_file = create_source_file(
            source_file="",
        )

        with self.assertRaises(ValidationError):
            source_file.full_clean()