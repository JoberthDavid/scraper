from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine

from scraper.settings import default_dburl, DATABASES, dburl

from core.models import SourceFile, Composition, InputItem, GenericItem, GenericDescription, Unit, UnitaryPrice, UnitaryCost, ProductiveCost, UnproductiveCost
from core.usefuls.choices import ANALITICO, SINTETICO, EQUIPAMENTO, MAODEOBRA, MATERIAL, AUXILIAR, TEMPO_FIXO, TRANSPORTE
from core.usefuls.pattern import *
from core.usefuls.regex_pattern import CompositionRegex


class FileXlsxProcessor:

    def __init__(self, response: dict, type_file: str, source_file: SourceFile) -> None:
        self.list_init()
        self.switch_type_file( type_file=type_file, response=response, source_file=source_file )

    def list_init(self):
        ###### inicialização das listas que serão necessárias         
        self.generic_item_bulk_create_list = []
        self.generic_description_bulk_create_list = []
        self.generic_item_in_bulk_list = []
        self.generic_item_pk_list = []
        self.generic_description_pk_list = []
        self.generic_item_manytomany = []
        self.generic_description_manytomany = []
        self.unitary_price_or_cost_bulk_create_list = []
        self.unitary_productive_cost_bulk_create_list = []
        self.unitary_unproductive_cost_bulk_create_list = []

    def create_instancies_of_unit_and_generic_item(self, data_frame, group):
    ###### criação das instâncias Unit e GenericItem
        for index, row in data_frame.iterrows():
            unit, created = Unit.objects.get_or_create(
                unit=row["unit"]
            )
            self.generic_item_bulk_create_list.append( GenericItem(
                code = row["code"],
                unit = unit,
                group = group,
                )
            )
            self.generic_item_in_bulk_list.append( row["code"] )
        GenericItem.objects.bulk_create( self.generic_item_bulk_create_list, ignore_conflicts=True )

    def create_instancies_of_generic_item(self, data_frame, group):
    ###### criação das instâncias GenericItem
        unit, created = Unit.objects.get_or_create(
            unit='h'
        )
        for index, row in data_frame.iterrows():
            self.generic_item_bulk_create_list.append( GenericItem(
                code = row["code"],
                unit = unit,
                group = group,
                )
            )
            self.generic_item_in_bulk_list.append( row["code"] )
        GenericItem.objects.bulk_create( self.generic_item_bulk_create_list, ignore_conflicts=True )

    def create_instancies_of_generic_description_and_unitary_price(self, data_frame, source_file):
    ###### criação das instâncias GenericDescription e UnitaryPrice
        for index, row in data_frame.iterrows():
            generic_item = GenericItem.objects.get(code=row["code"])
            self.generic_item_pk_list.append( generic_item.pk )
            self.generic_description_bulk_create_list.append( GenericDescription(
                generic_item = generic_item,
                description = row["description"],
                )
            )
            self.unitary_price_or_cost_bulk_create_list.append( UnitaryPrice(
                generic_item = generic_item,
                source_file = source_file,
                unitary_price = row["price"],
                )
            )
        GenericDescription.objects.bulk_create( self.generic_description_bulk_create_list, ignore_conflicts=True )
        UnitaryPrice.objects.bulk_create( self.unitary_price_or_cost_bulk_create_list, ignore_conflicts=True )

    def create_instancies_of_generic_description_and_unitary_cost(self, data_frame, source_file):
    ###### criação das instâncias GenericDescription e UnitaryCost
        for index, row in data_frame.iterrows():
            generic_item = GenericItem.objects.get(code=row["code"])
            self.generic_item_pk_list.append( generic_item.pk )
            self.generic_description_bulk_create_list.append( GenericDescription(
                generic_item = generic_item,
                description = row["description"],
                )
            )
            self.unitary_price_or_cost_bulk_create_list.append( UnitaryCost(
                generic_item = generic_item,
                source_file = source_file,
                unitary_cost = row["cost"],
                )
            )
        GenericDescription.objects.bulk_create( self.generic_description_bulk_create_list, ignore_conflicts=True )
        UnitaryCost.objects.bulk_create( self.unitary_price_or_cost_bulk_create_list, ignore_conflicts=True )

    def create_instancies_of_generic_description_and_costs(self, data_frame, source_file):
    ###### criação das instâncias GenericDescription, ProductiveCost e UnproductiveCost
        for index, row in data_frame.iterrows():
            generic_item = GenericItem.objects.get(code=row["code"])
            self.generic_item_pk_list.append( generic_item.pk )
            self.generic_description_bulk_create_list.append( GenericDescription(
                generic_item = generic_item,
                description = row["description"],
                )
            )
            self.unitary_productive_cost_bulk_create_list.append( ProductiveCost(
                generic_item = generic_item,
                source_file = source_file,
                productive_cost = row["productive_cost"],
                )
            )
            self.unitary_unproductive_cost_bulk_create_list.append( UnproductiveCost(
                generic_item = generic_item,
                source_file = source_file,
                unproductive_cost = row["unproductive_cost"],
                )
            )
        GenericDescription.objects.bulk_create( self.generic_description_bulk_create_list, ignore_conflicts=True )
        ProductiveCost.objects.bulk_create( self.unitary_productive_cost_bulk_create_list, ignore_conflicts=True )
        UnproductiveCost.objects.bulk_create( self.unitary_unproductive_cost_bulk_create_list, ignore_conflicts=True )
 
    def populate_list_with_pk_of_generic_description(self, data_frame):
    ###### criação da lista de pk GenericDescription
        for index, row in data_frame.iterrows():
            generic_description = GenericDescription.objects.get(description=row["description"])
            self.generic_description_pk_list.append( generic_description.pk )

    def recover_list_of_instancies_at_generic_item(self):
    ###### criação da lista de instâncias GenericItem
        return GenericItem.objects.in_bulk( self.generic_item_pk_list )

    def recover_list_of_instancies_at_generic_description(self):
    ###### criação da lista de instâncias GenericDescription
        return GenericDescription.objects.in_bulk( self.generic_description_pk_list )

    def relate_many_to_many_generic_description_with_source_file(self, descriptions, source_file):
    ###### criação das instâncias de relacionamento manytomany entre GenericDescription e SourceFile
        for description in descriptions:
            self.generic_description_manytomany.append(GenericDescription.source_files.through(
                genericdescription_id = description,
                sourcefile_id = source_file.pk,
                )
            )
        GenericDescription.source_files.through.objects.bulk_create( self.generic_description_manytomany, ignore_conflicts=True )

    def relate_many_to_many_generic_item_with_source_file(self, items, source_file):
    ###### criação das instâncias de relacionamento manytomany entre GenericItem e SourceFile
            for item in items:
                self.generic_item_manytomany.append(GenericItem.source_files.through(
                    genericitem_id = item,
                    sourcefile_id = source_file.pk,
                    )
                )
            GenericItem.source_files.through.objects.bulk_create( self.generic_item_manytomany, ignore_conflicts=True )

    def switch_type_file(self, type_file, response, source_file):
        if type_file == ANALITICO:

            print("OK")

        elif type_file == SINTETICO:
            data_frame = pd.read_excel(response["Body"].read(), names=['code', 'description', 'unit', 'price'], converters={'code':str, 'description':str, 'unit':str, 'price':float}, skiprows=source_file.number_of_lines_to_skip)

            self.create_instancies_of_unit_and_generic_item(data_frame, type_file)
            self.create_instancies_of_generic_description_and_unitary_price(data_frame, source_file)
            self.populate_list_with_pk_of_generic_description(data_frame)

            items = self.recover_list_of_instancies_at_generic_item()
            descriptions = self.recover_list_of_instancies_at_generic_description()

            self.relate_many_to_many_generic_description_with_source_file(descriptions, source_file)
            self.relate_many_to_many_generic_item_with_source_file(items, source_file)

        elif type_file == EQUIPAMENTO:
            data_frame = pd.read_excel(response["Body"].read(), names=['code', 'description', 'purchase_value', 'deprecation', 'equity_opportunity', 'insurance_and_taxes', 'maintenance', 'operation', 'labor', 'productive_cost', 'unproductive_cost'], converters={'code':str, 'description':str, 'purchase_value':float, 'deprecation':float, 'equity_opportunity':float, 'insurance_and_taxes':float, 'maintenance':float, 'operation':float, 'labor':float, 'productive_cost':float, 'unproductive_cost':float}, skiprows=source_file.number_of_lines_to_skip)

            self.create_instancies_of_generic_item(data_frame, type_file)
            self.create_instancies_of_generic_description_and_costs(data_frame, source_file)
            self.populate_list_with_pk_of_generic_description(data_frame)

            items = self.recover_list_of_instancies_at_generic_item()
            descriptions = self.recover_list_of_instancies_at_generic_description()

            self.relate_many_to_many_generic_description_with_source_file(descriptions, source_file)
            self.relate_many_to_many_generic_item_with_source_file(items, source_file)

        elif type_file == MAODEOBRA:
            data_frame = pd.read_excel(response["Body"].read(), names=['code', 'description', 'unit', 'wage', 'charges', 'cost', 'unhealthy'], converters={'code':str, 'description':str, 'unit':str, 'wage':float, 'charges':float, 'cost':float, 'unhealthy':float}, skiprows=source_file.number_of_lines_to_skip)

            self.create_instancies_of_unit_and_generic_item(data_frame, type_file)
            self.create_instancies_of_generic_description_and_unitary_cost(data_frame, source_file)
            self.populate_list_with_pk_of_generic_description(data_frame)

            items = self.recover_list_of_instancies_at_generic_item()
            descriptions = self.recover_list_of_instancies_at_generic_description()

            self.relate_many_to_many_generic_description_with_source_file(descriptions, source_file)
            self.relate_many_to_many_generic_item_with_source_file(items, source_file)

        elif type_file == MATERIAL:
            data_frame = pd.read_excel(response["Body"].read(), names=['code', 'description', 'unit', 'cost'], converters={'code':str, 'description':str, 'unit':str}, skiprows=source_file.number_of_lines_to_skip)

            data_frame['cost'].replace(['-'], [0.0], inplace=True)

            data_frame['cost'] = data_frame['cost'].astype(float)

            self.create_instancies_of_unit_and_generic_item(data_frame, type_file)
            self.create_instancies_of_generic_description_and_unitary_cost(data_frame, source_file)
            self.populate_list_with_pk_of_generic_description(data_frame)

            items = self.recover_list_of_instancies_at_generic_item()
            descriptions = self.recover_list_of_instancies_at_generic_description()

            self.relate_many_to_many_generic_description_with_source_file(descriptions, source_file)
            self.relate_many_to_many_generic_item_with_source_file(items, source_file)