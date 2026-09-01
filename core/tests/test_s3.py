import uuid

import pytest

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class TestS3Integration:
    """
    Integration tests for the configured S3 storage backend.

    These tests intentionally use pytest because they verify the
    real storage backend instead of the Django test database.
    """

    @pytest.mark.s3
    def test_save_and_retrieve_file(self):
        file_name = (
            f"testes/integracao/{uuid.uuid4()}/teste-s3.txt"
        )

        original_content = (
            b"Teste de integracao Django com AWS S3"
        )

        try:
            saved_name = default_storage.save(
                file_name,
                ContentFile(original_content),
            )

            assert saved_name == file_name
            assert default_storage.exists(saved_name)

            with default_storage.open(
                saved_name,
                "rb",
            ) as saved_file:
                retrieved_content = saved_file.read()

            assert retrieved_content == original_content

        finally:
            if default_storage.exists(file_name):
                default_storage.delete(file_name)