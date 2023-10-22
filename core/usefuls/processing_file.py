from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine

from scraper.settings import default_dburl, DATABASES, dburl

from core.models import SourceFile, Composition, InputItem, GenericItem, GenericDescription, Unit, UnitaryPrice
from core.usefuls.choices import ANALITICO, SINTETICO, EQUIPAMENTO, MAODEOBRA, MATERIAL, AUXILIAR, TEMPO_FIXO, TRANSPORTE
from core.usefuls.pattern import *
from core.usefuls.regex_pattern import CompositionRegex


class FileXlsxProcessor:

    def __init__(self, response: dict, type_file: str, source_file: SourceFile) -> None:
        self.switch_type_file( type_file=type_file, response=response, source_file=source_file )

    def switch_type_file(self, type_file, response, source_file):
        if type_file == ANALITICO:

            print("OK")

        elif type_file == SINTETICO:
            data_frame = pd.read_excel(response["Body"].read(), names=['code', 'description', 'unit', 'price'], converters={'code':str, 'description':str, 'unit':str, 'price':float}, skiprows=source_file.number_of_lines_to_skip)

###### inicialização das listas que serão necessárias         
            generic_group_bulk_create_list = []
            description_bulk_create_list = []
            in_bulk_list = []

            list_object_generic_item = []
            list_object_generic_description = []
            
            generic_item_manytomany = []
            generic_description_manytomany = []

            unit_cost_price_bulk_create_list = []

###### criação das instâncias Unit e GenericItem

            for index, row in data_frame.iterrows():

                unit, created = Unit.objects.get_or_create(
                    unit=row["unit"]
                )

                generic_group_bulk_create_list.append( GenericItem(
                    code = row["code"],
                    unit = unit,
                    group = SINTETICO,
                    )
                )
                in_bulk_list.append( row["code"] )

            result_generic_item_created = GenericItem.objects.bulk_create( generic_group_bulk_create_list, ignore_conflicts=True )

###### criação das instâncias GenericDescription

            for index, row in data_frame.iterrows():

                generic_item = GenericItem.objects.get(code=row["code"])
                list_object_generic_item.append( generic_item.pk )

                description_bulk_create_list.append( GenericDescription(
                    generic_item = generic_item,
                    description = row["description"],
                    )
                )

            inbulk_result = list( GenericItem.objects.in_bulk(in_bulk_list, field_name="code").values() )

            result_generic_description_created = GenericDescription.objects.bulk_create( description_bulk_create_list, ignore_conflicts=True )

###### criação da lista de instâncias GenericDescription

            for index, row in data_frame.iterrows():

                generic_description = GenericDescription.objects.get(description=row["description"])
                list_object_generic_description.append( generic_description.pk )
                
###### criação da lista de instâncias GenericItem

            items = GenericItem.objects.in_bulk( list_object_generic_item )
            descriptions = GenericDescription.objects.in_bulk( list_object_generic_description )

###### criação das instâncias de relacionamento manytomany entre GenericDescription e SourceFile

            for description in descriptions:

                generic_description_manytomany.append(GenericDescription.source_files.through(
                    genericdescription_id = description,
                    sourcefile_id = source_file.pk,
                    )
                )

            result_manytomany_description_created = GenericDescription.source_files.through.objects.bulk_create( generic_description_manytomany, ignore_conflicts=True )

###### criação das instâncias de relacionamento manytomany entre GenericItem e SourceFile

            for item in items:

                generic_item_manytomany.append(GenericItem.source_files.through(
                    genericitem_id = item,
                    sourcefile_id = source_file.pk,
                    )
                )

            result_manytomany_item_created = GenericItem.source_files.through.objects.bulk_create( generic_item_manytomany, ignore_conflicts=True )

###### criação das instâncias UnitaryCostPrice

            for index, row in data_frame.iterrows():

                generic_item = GenericItem.objects.get(code=row["code"])

                unit_cost_price_bulk_create_list.append( UnitaryPrice(
                    generic_item = generic_item,
                    source_file = source_file,
                    unitary_price = row["price"],
                    )
                )

            result_unit_cost_price_created = UnitaryPrice.objects.bulk_create( unit_cost_price_bulk_create_list, ignore_conflicts=True )



        elif type_file == EQUIPAMENTO:
            print('Equipamento')
            print(data_frame)
        elif type_file == MAODEOBRA:
            data_frame = pd.read_excel(response["Body"].read(), names=['code', 'description', 'unit', 'wage', 'charges', 'cost', 'unhealthy'], converters={'code':str, 'description':str, 'unit':str, 'wage':float, 'charges':float, 'cost':float, 'unhealthy':float}, skiprows=4)
            
            # generic_group_bulk_create_list = []
            # print('Mão de obra')
            print(data_frame)
        elif type_file == MATERIAL:
            print('Material')
            print(data_frame)