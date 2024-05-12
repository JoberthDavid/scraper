import datetime
from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.contrib.admin import *

from core.usefuls.choices import *
from core.models import *
from core.usefuls.processing_file import FileXlsxProcessor

import pandas as pd

from io import BytesIO
import boto3
from scraper.settings import AWS_STORAGE_BUCKET_NAME


data_base = '2023-07-01'
file_for_workmen = "./core/file_uploaded/DF 07-2023 Relatório Sintético de M╞o de Obra.xlsx"
unit = 'h'
dimensional = None
code = 'P9821'
description = 'Pedreiro'
group = MAODEOBRA


class SourceFileTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        """Must setUp response_upload_app"""
        SourceFile.objects.create(data_base=data_base, source_file=file_for_workmen, type_file=MAODEOBRA)
    
    def test_get_absolute_url(self):
        """Must return absolute url by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        self.assertEqual(source_file.get_absolute_url(), '/scraper/1/')

    def test_str(self):
        """Must return str method by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        self.assertEqual(source_file.__str__(), " - ".join([source_file.methodology, source_file.uf, source_file.parser_data_base_to_string(), source_file.type_system, source_file.type_file]) )

    def test_methodology_label(self):
        """Must return correct methodology field by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        field_label = source_file._meta.get_field('methodology').verbose_name
        self.assertEqual(field_label, 'Metodologia')

    def test_data_base_label(self):
        """Must return correct data_base field by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        field_label = source_file._meta.get_field('data_base').verbose_name
        self.assertEqual(field_label, 'Data-base')

    def test_file_label(self):
        """Must return correct file field by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        field_label = source_file._meta.get_field('source_file').verbose_name
        self.assertEqual(field_label, 'Arquivo de origem')

    def test_uf_label(self):
        """Must return correct uf field by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        field_label = source_file._meta.get_field('uf').verbose_name
        self.assertEqual(field_label, 'UF')

    def test_type_system_label(self):
        """Must return correct type_system field by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        field_label = source_file._meta.get_field('type_system').verbose_name
        self.assertEqual(field_label, 'Tipo de sistema')

    def test_type_file_label(self):
        """Must return correct type_file field by SourceFile"""
        source_file = SourceFile.objects.get(id=1)
        field_label = source_file._meta.get_field('type_file').verbose_name
        self.assertEqual(field_label, 'Tipo de arquivo')


class UnitTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        """Must setUp response_upload_app"""
        Unit.objects.create(unit=unit, dimensional=dimensional)

    def test_str(self):
        """Must return str method by Unit"""
        unit = Unit.objects.get(id=1)
        self.assertEqual(unit.__str__(), str(unit.unit) )


class GenericItemTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        """Must setUp response_upload_app"""
        GenericItem.objects.create(code=code)

    def test_str(self):
        """Must return str method by GenericItem"""
        generic_item = GenericItem.objects.get(id=1)
        self.assertEqual(generic_item.__str__(), str(generic_item.code) )


class GenericDescriptionTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        """Must setUp response_upload_app"""
        GenericDescription.objects.create(description=description, group=group)

    def test_str(self):
        """Must return str method by GenericDescription"""
        generic_description = GenericDescription.objects.get(id=1)
        self.assertEqual(generic_description.__str__(), str(generic_description.description) )    
    

class SourceFileAdminTests(TestCase):

    def setUp(self):
        """Must create some object to perform the action on"""
        self.source_file = SourceFile.objects.create(
                                                    data_base=datetime.date(2023,7,1),
                                                    source_file=file_for_workmen,
                                                    type_file=MAODEOBRA,
                                                    number_of_lines_to_skip=4,
                                                    status=False,
                                                    uf=DISTRITO_FEDERAL,
                                                    type_system=ONERADO,
                                                    methodology=SICRO,
                                                    )
        """Must create auth user for views using api request factory"""
        self.username = 'source_file_tester'
        self.password = '123'
        self.user = User.objects.create_superuser(self.username, 'source_file_tester@example.com', self.password)

    def test_action_file_processor(self):
        """Must do the action on the selected object"""
        data = {'action': 'process_file', 'Body':[self.source_file.pk,]}
        change_url = reverse('admin:%s_%s_changelist' % (SourceFile._meta.app_label, SourceFile._meta.model_name) )
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()
        self.assertEqual(response.status_code, 200)