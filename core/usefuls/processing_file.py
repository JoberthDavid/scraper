from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine

from scraper.settings import default_dburl, DATABASES, dburl

from core.models import SourceFile, Composition, InputItem, GenericItem, GenericDescription, Unit, MonetaryValue
from core.usefuls.choices import *


class FileXlsxProcessor:

    def __init__(self, response: dict, type_file: str, source_file: SourceFile) -> None:
        self.list_init()
        self.process_source_file( type_file=type_file, response=response, source_file=source_file )

    def list_init(self):
        ###### inicialização das listas necessárias
        self.generic_item_pk_list = []
        self.generic_description_pk_list = []

    def create_instancies_of_unit(self, data_frame):
    ###### criação das instâncias Unit
        for index, row in data_frame.iterrows():
            object, created = Unit.objects.get_or_create(
                unit=row[df_unit]
            )

    def get_dictionary_of_unit(self):
    ###### retorno de dicionários de instâncias Unit
        return Unit.objects.all().in_bulk( field_name=df_unit )

    def create_instancies_of_generic_item(self, data_frame, group):
    ###### criação das instâncias GenericItem
        generic_item_bulk_create_list = []
        for index, row in data_frame.iterrows():
            generic_item_bulk_create_list.append( GenericItem(
                code = row[df_code],
                group = group,
                )
            )
        GenericItem.objects.bulk_create( generic_item_bulk_create_list, ignore_conflicts=True )

    def create_instancies_of_generic_description(self, data_frame, group):
    ###### criação das instâncias GenericDescription
        generic_description_bulk_create_list = []
        for index, row in data_frame.iterrows():
            generic_item = GenericItem.objects.get(code=row[df_code])
            self.generic_item_pk_list.append( generic_item.pk )
            generic_description_bulk_create_list.append( GenericDescription(
                generic_item = generic_item,
                description = row[df_description],
                group = group,
                )
            )
        GenericDescription.objects.bulk_create( generic_description_bulk_create_list, ignore_conflicts=True )
 
    def create_instancies_of_monetary_value(self, data_frame, group, source_file, dict_of_unit, classification, monetary_value=df_monetary_value):
    ###### criação das instâncias MonetaryValue
        monetary_value_bulk_create_list = []
        for index, row in data_frame.iterrows():
            generic_item = GenericItem.objects.get(code=row[df_code])
            monetary_value_bulk_create_list.append( MonetaryValue(
                generic_item = generic_item,
                source_file = source_file,
                unit = dict_of_unit[row[df_unit]],
                monetary_value = row[monetary_value],
                classification = classification,
                group = group,
                )
            )
        MonetaryValue.objects.bulk_create( monetary_value_bulk_create_list, ignore_conflicts=True )

    def populate_list_with_pk_of_generic_description(self, data_frame):
    ###### criação da lista de pk GenericDescription
        for index, row in data_frame.iterrows():
            generic_description = GenericDescription.objects.get(description=row[df_description])
            self.generic_description_pk_list.append( generic_description.pk )

    def recover_list_of_instancies_at_generic_item(self):
    ###### criação da lista de instâncias GenericItem
        return GenericItem.objects.in_bulk( self.generic_item_pk_list )

    def recover_list_of_instancies_at_generic_description(self):
    ###### criação da lista de instâncias GenericDescription
        return GenericDescription.objects.in_bulk( self.generic_description_pk_list )

    def relate_many_to_many_generic_item_with_source_file(self, items, source_file):
    ###### criação das instâncias de relacionamento manytomany entre GenericItem e SourceFile
        generic_item_manytomany = []
        for item in items:
            generic_item_manytomany.append(GenericItem.source_files.through(
                genericitem_id = item,
                sourcefile_id = source_file.pk,
                )
            )
        GenericItem.source_files.through.objects.bulk_create( generic_item_manytomany, ignore_conflicts=True )

    def relate_many_to_many_generic_description_with_source_file(self, descriptions, source_file):
    ###### criação das instâncias de relacionamento manytomany entre GenericDescription e SourceFile
        generic_description_manytomany = []
        for description in descriptions:
            generic_description_manytomany.append(GenericDescription.source_files.through(
                genericdescription_id = description,
                sourcefile_id = source_file.pk,
                )
            )
        GenericDescription.source_files.through.objects.bulk_create( generic_description_manytomany, ignore_conflicts=True )

    def get_prepared_data_frame(self, type_file, response, source_file):
        if type_file == ANALITICO:
            data_frame = pd.read_excel(response[df_body].read(), names=[df_code, df_description, df_quantity, df_productive_use, df_unproductive_use, df_productive_cost, df_unproductive_cost, df_production, df_unit])
            data_frame[df_production].fillna(0.0, inplace=True)
        elif type_file == SINTETICO:
            data_frame = pd.read_excel(response[df_body].read(), names=[df_code, df_description, df_unit, df_monetary_value], converters={df_code:str, df_description:str, df_unit:str, df_monetary_value:float}, skiprows=source_file.number_of_lines_to_skip)        
        elif type_file == EQUIPAMENTO:
            data_frame = pd.read_excel(response[df_body].read(), names=[df_code, df_description, df_purchase_value, df_deprecation, df_equity_opportunity, df_insurance_and_taxes, df_maintenance, df_operation, df_labor, df_productive_cost, df_unproductive_cost], converters={df_code:str, df_description:str, df_purchase_value:float, df_deprecation:float, df_equity_opportunity:float, df_insurance_and_taxes:float, df_maintenance:float, df_operation:float, df_labor:float, df_productive_cost:float, df_unproductive_cost:float}, skiprows=source_file.number_of_lines_to_skip).assign(unit="h")        
        elif type_file == MAODEOBRA:
            data_frame = pd.read_excel(response[df_body].read(), names=[df_code, df_description, df_unit, df_wage, df_charges, df_monetary_value, df_unhealthy], converters={df_code:str, df_description:str, df_unit:str, df_wage:float, df_charges:float, df_monetary_value:float, df_unhealthy:float}, skiprows=source_file.number_of_lines_to_skip)        
        elif type_file == MATERIAL:
            data_frame = pd.read_excel(response[df_body].read(), names=[df_code, df_description, df_unit, df_monetary_value], converters={df_code:str, df_description:str, df_unit:str}, skiprows=source_file.number_of_lines_to_skip)
            data_frame[df_monetary_value].replace(['-'], [0.0], inplace=True)
            data_frame[df_monetary_value] = data_frame[df_monetary_value].astype(float)
        return data_frame

    def switch_monetary_value(self, data_frame, type_file, source_file, dict_of_unit):
        if type_file == SINTETICO:
            self.create_instancies_of_monetary_value(data_frame, type_file, source_file, dict_of_unit, PRECO)
        elif type_file == EQUIPAMENTO:
            self.create_instancies_of_monetary_value(data_frame, type_file, source_file, dict_of_unit, PRODUTIVO, monetary_value=df_productive_cost)
            self.create_instancies_of_monetary_value(data_frame, type_file, source_file, dict_of_unit, IMPRODUTIVO, monetary_value=df_unproductive_cost)
        elif type_file == MAODEOBRA or type_file == MATERIAL:
            self.create_instancies_of_monetary_value(data_frame, type_file, source_file, dict_of_unit, CUSTO)

    def get_dictionary_of_generic_item(self):
    ###### retorno de dicionários de instâncias GenericItem
        return GenericItem.objects.filter(group=SINTETICO).in_bulk( field_name=df_code )

    def get_dictionary_of_generic_description(self):
    ###### retorno de dicionários de instâncias GenericDescription
        return GenericDescription.objects.all().in_bulk( field_name=df_description )

    def scrape_multiple_basic_data_from_analitic_composition(self, source_file, data_frame):
        code_list_from_analitic_composition = []
        description_list_from_analitic_composition = []
        production_list_from_analitic_composition = []
        unit_list_from_analitic_composition = []
        fic_list_from_analitic_composition = []
        group_list_from_analitic_composition = []
        dict_of_unit = self.get_dictionary_of_unit()
        dict_of_generic_item = self.get_dictionary_of_generic_item()
        dict_of_generic_description = self.get_dictionary_of_generic_description()
        composition_bulk_create_list = []
        for index, row in data_frame.iterrows():
            if row[df_code] == "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS - SICRO":
                fic_list_from_analitic_composition.append(row[df_production])
            elif row[df_code] == "Custo Unitário de Referência":
                production_list_from_analitic_composition.append(row[df_production])
                unit_list_from_analitic_composition.append(dict_of_unit[row[df_unit]])
            elif row[df_production] == "Valores em reais (R$)":
                code_list_from_analitic_composition.append(dict_of_generic_item[row[df_code]])
                # description_list_from_analitic_composition.append( GenericDescription.objects.get( description=row[df_description] ) )
                description_list_from_analitic_composition.append(dict_of_generic_description[row[df_description]])
                group_list_from_analitic_composition.append(row[df_code][:2])
        
        for index, code in enumerate(code_list_from_analitic_composition):
            composition_bulk_create_list.append( Composition(
                generic_item = code,
                generic_description = description_list_from_analitic_composition[index],
                unit=unit_list_from_analitic_composition[index],
                fic=fic_list_from_analitic_composition[index],
                production=production_list_from_analitic_composition[index],
                source_file=source_file,
                composition_group=group_list_from_analitic_composition[index],
                )
            )
        Composition.objects.bulk_create( composition_bulk_create_list, ignore_conflicts=True )

    def process_source_file(self, type_file, response, source_file):
        if type_file == ANALITICO:
            data_frame = self.get_prepared_data_frame(type_file, response, source_file)
            self.scrape_multiple_basic_data_from_analitic_composition(source_file, data_frame)
        else:
            data_frame = self.get_prepared_data_frame(type_file, response, source_file)
            self.create_instancies_of_unit(data_frame)
            dict_of_unit = self.get_dictionary_of_unit()
            self.create_instancies_of_generic_item(data_frame, type_file)
            self.create_instancies_of_generic_description(data_frame, type_file)
            self.switch_monetary_value(data_frame, type_file, source_file, dict_of_unit)
            self.populate_list_with_pk_of_generic_description(data_frame)
            items = self.recover_list_of_instancies_at_generic_item()
            descriptions = self.recover_list_of_instancies_at_generic_description()
            self.relate_many_to_many_generic_description_with_source_file(descriptions, source_file)
            self.relate_many_to_many_generic_item_with_source_file(items, source_file)