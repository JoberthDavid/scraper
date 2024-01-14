from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine

from scraper.settings import default_dburl, DATABASES, dburl

from core.models import SourceFile, Composition, EquipmentItem, WorkmanItem, MaterialItem, AuxiliaryActivityItem, TransportItem, GenericItem, GenericDescription, Unit, MonetaryValue
from core.usefuls.choices import *
import re

from django.db.models import Prefetch
from django.db.models import Q

from django.db import connection, reset_queries
import time


class FileXlsxProcessor:

    def __init__(self, response: dict, type_file: str, source_file: SourceFile) -> None:
        self.process_source_file( type_file=type_file, response=response, source_file=source_file )

    def get_or_create_instancies_of_unit(self, data_frame):
    ###### criação das instâncias Unit
        for index, row in data_frame.iterrows():
            object, created = Unit.objects.get_or_create(
                unit=row[df_unit],
                dimensional=None,
            )

    def get_collection_of_unit(self):
    ###### retorno de coleção de instâncias Unit
        return Unit.objects.all().in_bulk( field_name=df_unit )

    def create_instancies_of_generic_item(self, data_frame, type_file):
    ###### criação das instâncias GenericItem
        generic_item_bulk_create_list = []
        for index, row in data_frame.iterrows():
            generic_item_bulk_create_list.append( GenericItem(
                code = row[df_code],
                )
            )
        GenericItem.objects.bulk_create( generic_item_bulk_create_list, ignore_conflicts=True )

    def create_instancies_of_generic_description(self, data_frame, type_file):
    ###### criação das instâncias GenericDescription
        generic_description_bulk_create_list = []
        if type_file == SINTETICO:
            group = COMPOSICAO
        else:
            group = type_file
        for index, row in data_frame.iterrows():
            generic_description_bulk_create_list.append( GenericDescription(
                description = row[df_description],
                group = group,
                )
            )
        GenericDescription.objects.bulk_create( generic_description_bulk_create_list, ignore_conflicts=True )
 
    def create_instancies_of_monetary_value(self, collection_of_related_items, data_frame, type_file, source_file, collection_of_unit, classification, monetary_value=df_monetary_value):
    ###### criação das instâncias MonetaryValue
        monetary_value_bulk_create_list = []
        if type_file == SINTETICO:
            group = COMPOSICAO
        else:
            group = type_file
        for index, row in data_frame.iterrows():
            monetary_value_bulk_create_list.append( MonetaryValue(
                generic_item = collection_of_related_items[row[df_code]],
                source_file = source_file,
                unit = collection_of_unit[row[df_unit]],
                monetary_value = row[monetary_value],
                classification = classification,
                group = group,
                type_system = source_file.type_system,
                )
            )
        MonetaryValue.objects.bulk_create( monetary_value_bulk_create_list, ignore_conflicts=True )

    def get_collection_of_generic_item_unrelated(self):
    ###### retorno de coleção de instâncias GenericItem sem relacionamentos construídos
        return GenericItem.objects.in_bulk(field_name='code')

    def get_collection_of_generic_description_unrelated(self):
    ###### retorno de coleção de instâncias GenericDescription sem relacionamentos construídos
        return GenericDescription.objects.in_bulk(field_name='description')

    def relate_many_to_many_generic_item_with_source_file(self, data_frame, collection_of_unrelated_items, source_file):
    ###### criação das instâncias de relacionamento manytomany entre GenericItem e SourceFile
        generic_item_manytomany = []
        for index, row in data_frame.iterrows():
            generic_item_manytomany.append(GenericItem.source_files.through(
                genericitem_id = collection_of_unrelated_items[ row[df_code] ].pk,
                sourcefile_id = source_file.pk,
                )
            )
        GenericItem.source_files.through.objects.bulk_create( generic_item_manytomany, ignore_conflicts=True )

    def get_collection_of_generic_item_related_with_source_file(self, field, source_file, group=None):
    ###### retorno de coleção de instâncias GenericItem
        if not(group):
            return GenericItem.objects.filter(source_files__data_base=source_file.data_base).in_bulk( field_name=field )
        elif group == COMPOSICAO:
            return GenericItem.objects.filter(source_files__data_base=source_file.data_base).filter(source_files__type_file=SINTETICO).in_bulk( field_name=field )
        else:
            return GenericItem.objects.filter(source_files__data_base=source_file.data_base).filter(source_files__type_file=group).in_bulk( field_name=field )

    def get_collection_of_generic_description_related_with_source_file(self, field, source_file):
    ###### retorno de coleção de instâncias GenericDescription
        return GenericDescription.objects.filter(source_files__data_base=source_file.data_base).in_bulk( field_name=field )

    def relate_many_to_many_generic_description_with_source_file(self, data_frame, collection_of_unrelated_descriptions, source_file):
    ###### criação das instâncias de relacionamento manytomany entre GenericDescription e SourceFile
        generic_description_manytomany_with_source_file = []
        for index, row in data_frame.iterrows():
            generic_description_manytomany_with_source_file.append(GenericDescription.source_files.through(
                genericdescription_id = collection_of_unrelated_descriptions[ row[df_description] ].pk,
                sourcefile_id = source_file.pk,
                )
            )
        GenericDescription.source_files.through.objects.bulk_create( generic_description_manytomany_with_source_file, ignore_conflicts=True )

    def relate_many_to_many_generic_description_with_generic_item(self, data_frame, collection_of_related_items, collection_of_related_descriptions):
    ###### criação das instâncias de relacionamento manytomany entre GenericDescription e GenericItem
        generic_description_manytomany_with_generic_item = []
        for index, row in data_frame.iterrows():
            generic_description_manytomany_with_generic_item.append(GenericDescription.generic_items.through(
                genericdescription_id = collection_of_related_descriptions[ row[df_description] ].pk,
                genericitem_id = collection_of_related_items[ row[df_code] ].pk,
                )
            )
        GenericDescription.generic_items.through.objects.bulk_create( generic_description_manytomany_with_generic_item, ignore_conflicts=True )

    def get_prepared_data_frame(self, type_file, response, source_file):
        if type_file == ANALITICO:
            data_frame = pd.read_excel(response[df_body].read(), names=[df_code, df_description, df_quantity, df_productive_use, df_unproductive_use, df_productive_cost, df_unproductive_cost, df_production, df_unit] )
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

    def switch_monetary_value(self, collection_of_related_items, data_frame, type_file, source_file, collection_of_unit):
        if type_file == SINTETICO:
            self.create_instancies_of_monetary_value(collection_of_related_items, data_frame, COMPOSICAO, source_file, collection_of_unit, PRECO)
        elif type_file == EQUIPAMENTO:
            self.create_instancies_of_monetary_value(collection_of_related_items, data_frame, type_file, source_file, collection_of_unit, PRODUTIVO, monetary_value=df_productive_cost)
            self.create_instancies_of_monetary_value(collection_of_related_items, data_frame, type_file, source_file, collection_of_unit, IMPRODUTIVO, monetary_value=df_unproductive_cost)
        elif type_file == MAODEOBRA or type_file == MATERIAL:
            self.create_instancies_of_monetary_value(collection_of_related_items, data_frame, type_file, source_file, collection_of_unit, CUSTO)

    def scrape_multiple_basic_data_from_analitic_composition(self, source_file, data_frame):
        code_list_from_analitic_composition = []
        description_list_from_analitic_composition = []
        production_list_from_analitic_composition = []
        unit_list_from_analitic_composition = []
        fic_list_from_analitic_composition = []
        group_list_from_analitic_composition = []

        collection_of_unit = self.get_collection_of_unit()
        collection_of_generic_item = self.get_collection_of_generic_item_related_with_source_file(field=df_code, source_file=source_file, group=COMPOSICAO)
        collection_of_generic_description = self.get_collection_of_generic_description_related_with_source_file(field=df_description, source_file=source_file)
        composition_bulk_create_list = []
        for index, row in data_frame.iterrows():
            if row[df_code] == "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS - SICRO":
                try:
                    fic_list_from_analitic_composition.append( row[df_production] )
                except:
                    break
            elif row[df_code] == "Custo Unitário de Referência":
                try:
                    production_list_from_analitic_composition.append( row[df_production] )
                    unit_list_from_analitic_composition.append(collection_of_unit[row[df_unit]] )
                except:
                    break
            elif row[df_production] == "Valores em reais (R$)":
                try:
                    code_list_from_analitic_composition.append(collection_of_generic_item[row[df_code]] )
                    description_list_from_analitic_composition.append(collection_of_generic_description[row[df_description]] )
                    group_list_from_analitic_composition.append( row[df_code][:2] )
                except:
                    break
        
        for index, code in enumerate(code_list_from_analitic_composition):
            composition_bulk_create_list.append( Composition(
                generic_item = code_list_from_analitic_composition[index],
                generic_description = description_list_from_analitic_composition[index],
                unit=unit_list_from_analitic_composition[index],
                fic=fic_list_from_analitic_composition[index],
                production=production_list_from_analitic_composition[index],
                composition_group=group_list_from_analitic_composition[index],
                )
            )
        Composition.objects.bulk_create( composition_bulk_create_list, ignore_conflicts=True )

    def get_collection_of_composition(self, source_file):
    ###### retorno de coleção de instâncias Composition
        return Composition.objects.select_related('generic_item').filter(generic_item__source_files__data_base=source_file.data_base).in_bulk()

    def relate_many_to_many_composition_with_source_file(self, compositions, source_file):
    ###### criação das instâncias de relacionamento manytomany entre Composition e SourceFile
        composition_manytomany_with_source_file = []
        for composition in compositions:
            composition_manytomany_with_source_file.append(Composition.source_files.through(
                composition_id = composition,
                sourcefile_id = source_file.pk,
                )
            )
        Composition.source_files.through.objects.bulk_create( composition_manytomany_with_source_file, ignore_conflicts=True )

    def scrape_multiple_input_data_from_analitic_composition(self, source_file, data_frame):

        composition_list_from_analitic_composition_for_equipment = []
        input_code_list_from_analitic_composition_for_equipment = []
        input_description_list_from_analitic_composition_for_equipment = []
        input_group_list_from_analitic_composition_for_equipment = []
        input_quantity_list_from_analitic_composition_for_equipment = []
        input_productive_use_list_from_analitic_composition_for_equipment = []
        input_unit_list_from_analitic_composition_for_equipment = []
        input_item_bulk_create_list_for_equipment = []

        composition_list_from_analitic_composition_for_workman = []
        input_code_list_from_analitic_composition_for_workman = []
        input_description_list_from_analitic_composition_for_workman = []
        input_group_list_from_analitic_composition_for_workman = []
        input_quantity_list_from_analitic_composition_for_workman = []
        input_unit_list_from_analitic_composition_for_workman = []
        input_item_bulk_create_list_for_workman = []

        composition_list_from_analitic_composition_for_material = []
        input_code_list_from_analitic_composition_for_material = []
        input_description_list_from_analitic_composition_for_material = []
        input_group_list_from_analitic_composition_for_material = []
        input_quantity_list_from_analitic_composition_for_material = []
        input_unit_list_from_analitic_composition_for_material = []
        input_item_bulk_create_list_for_material = []

        composition_list_from_analitic_composition_for_activity = []
        input_code_list_from_analitic_composition_for_activity = []
        input_description_list_from_analitic_composition_for_activity = []
        input_group_list_from_analitic_composition_for_activity = []
        input_quantity_list_from_analitic_composition_for_activity = []
        input_unit_list_from_analitic_composition_for_activity = []
        input_item_bulk_create_list_for_activity = []

        composition_list_from_analitic_composition_for_transport = []
        input_code_list_from_analitic_composition_for_transport = []
        input_description_list_from_analitic_composition_for_transport = []
        input_group_list_from_analitic_composition_for_transport = []
        input_quantity_list_from_analitic_composition_for_transport = []
        input_unit_list_from_analitic_composition_for_transport = []
        input_proprietary_code_list_from_analitic_composition_for_transport = []
        input_item_bulk_create_list_for_transport = []

        collection_of_unit = self.get_collection_of_unit()

        collection_of_code_and_description = {}
        items = GenericItem.objects.filter(source_files__data_base=source_file.data_base).prefetch_related('descriptions')
        for item in items:
            for description in item.descriptions.all():
                collection_of_code_and_description[item.code] = ( item, description )

        compositions = Composition.objects.filter( source_files=source_file.pk )
        prefetch1 = Prefetch('compositions', queryset=compositions, to_attr='compositions_list')
        collection_of_composition = {}
        items = GenericItem.objects.prefetch_related(prefetch1)
        for item in items:
            for composition in item.compositions_list:
                collection_of_composition[item.code] = composition

        for index, row in data_frame.iterrows():
            if row[df_production] == "Valores em reais (R$)":
                try:
                    composition = collection_of_composition[ row[df_code] ]
                except:
                    break

            elif re.match( r'[EA]\d{4}', str( row[df_code] ) ):
                try:
                    composition_list_from_analitic_composition_for_equipment.append( composition )
                    input_code_list_from_analitic_composition_for_equipment.append( collection_of_code_and_description[row[df_code]][0] )
                    input_description_list_from_analitic_composition_for_equipment.append( collection_of_code_and_description[row[df_code]][1] )
                    input_group_list_from_analitic_composition_for_equipment.append( EQUIPAMENTO )
                    input_quantity_list_from_analitic_composition_for_equipment.append( row[df_quantity] )
                    input_productive_use_list_from_analitic_composition_for_equipment.append( row[df_productive_use] )
                    input_unit_list_from_analitic_composition_for_equipment.append( collection_of_unit["h"] )
                except:
                    break

            elif re.match( r'[P]\d{4}', str( row[df_code] ) ):
                try:
                    composition_list_from_analitic_composition_for_workman.append( composition )
                    input_code_list_from_analitic_composition_for_workman.append( collection_of_code_and_description[row[df_code]][0] )
                    input_description_list_from_analitic_composition_for_workman.append( collection_of_code_and_description[row[df_code]][1] )
                    input_group_list_from_analitic_composition_for_workman.append( MAODEOBRA )
                    input_quantity_list_from_analitic_composition_for_workman.append( row[df_quantity] )
                    input_unit_list_from_analitic_composition_for_workman.append( collection_of_unit["h"] )
                except:
                    break

            elif re.match( r'[M]\d{4}', str( row[df_code] ) ) and ( type( row[df_productive_use] ) == str ) and not( re.match( r'\d{7}', str( row[df_unproductive_use] ) ) ) and not( re.match( r'\d{7}', str( row[df_production] ) ) ) :
                try:
                    composition_list_from_analitic_composition_for_material.append( composition )
                    input_code_list_from_analitic_composition_for_material.append( collection_of_code_and_description[row[df_code]][0] )
                    input_description_list_from_analitic_composition_for_material.append( collection_of_code_and_description[row[df_code]][1] )
                    input_group_list_from_analitic_composition_for_material.append( MATERIAL )
                    input_quantity_list_from_analitic_composition_for_material.append( row[df_quantity] )
                    input_unit_list_from_analitic_composition_for_material.append( collection_of_unit[row[df_productive_use]] )
                except:
                    break

            elif re.match( r'\d{7}', str( row[df_code] ) ) and ( type( row[df_productive_use] ) == str ) and not( re.match( r'\d{7}', str( row[df_unproductive_use] ) ) ) and not( re.match( r'\d{7}', str( row[df_production] ) ) ) :
                try:
                    composition_list_from_analitic_composition_for_activity.append( composition )
                    input_code_list_from_analitic_composition_for_activity.append( collection_of_code_and_description[row[df_code]][0] )
                    input_description_list_from_analitic_composition_for_activity.append( collection_of_code_and_description[row[df_code]][1] )
                    input_group_list_from_analitic_composition_for_activity.append( AUXILIAR )
                    input_quantity_list_from_analitic_composition_for_activity.append( row[df_quantity] )
                    input_unit_list_from_analitic_composition_for_activity.append( collection_of_unit[row[df_productive_use]] )
                except:
                    break

            elif re.match( r'\d{7}', str( row[df_quantity] ) ):
                try:
                    composition_list_from_analitic_composition_for_transport.append( composition )
                    input_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_quantity]][0] )
                    input_description_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_quantity]][1] )
                    input_group_list_from_analitic_composition_for_transport.append( TEMPO_FIXO )
                    input_quantity_list_from_analitic_composition_for_transport.append( row[df_productive_use] )
                    input_unit_list_from_analitic_composition_for_transport.append( collection_of_unit[row[df_unproductive_use]] )
                    input_proprietary_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_code]][0] )
                except:
                    break
                
            elif re.match( r'\d{7}', str( row[df_unproductive_use] ) ) and re.match( r'\d{7}', str( row[df_productive_cost] ) ) and re.match( r'\d{7}', str( row[df_unproductive_cost] ) ):
                try:
                    # first mean of transportation
                    composition_list_from_analitic_composition_for_transport.append( composition )
                    input_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_unproductive_use]][0] )
                    input_description_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_unproductive_use]][1] )
                    input_group_list_from_analitic_composition_for_transport.append( LEITO_NATURAL )
                    input_quantity_list_from_analitic_composition_for_transport.append( row[df_quantity] )
                    input_unit_list_from_analitic_composition_for_transport.append( collection_of_unit[row[df_productive_use]] )
                    input_proprietary_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_code]][0] )
                    # second mean of transportation
                    composition_list_from_analitic_composition_for_transport.append( composition )
                    input_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_productive_cost]][0] )
                    input_description_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_productive_cost]][1] )
                    input_group_list_from_analitic_composition_for_transport.append( REVESTIMENTO_PRIMARIO )
                    input_quantity_list_from_analitic_composition_for_transport.append( row[df_quantity] )
                    input_unit_list_from_analitic_composition_for_transport.append( collection_of_unit[row[df_productive_use]] )
                    input_proprietary_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_code]][0] )
                    # third mean of transportation
                    composition_list_from_analitic_composition_for_transport.append( composition )
                    input_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_unproductive_cost]][0] )
                    input_description_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_unproductive_cost]][1] )
                    input_group_list_from_analitic_composition_for_transport.append( PAVIMENTADO )
                    input_quantity_list_from_analitic_composition_for_transport.append( row[df_quantity] )
                    input_unit_list_from_analitic_composition_for_transport.append( collection_of_unit[row[df_productive_use]] )
                    input_proprietary_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_code]][0] )
                except:
                    break
                
            elif re.match( r'\d{7}', str( row[df_production] ) ) and ( type( row[df_productive_use] ) == str ):
                # fourth mean of transportation
                try:
                    composition_list_from_analitic_composition_for_transport.append( composition )
                    input_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_production]][0] )
                    input_description_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_production]][1] )
                    input_group_list_from_analitic_composition_for_transport.append( FERROVIARIO )
                    input_quantity_list_from_analitic_composition_for_transport.append( row[df_quantity] )
                    input_unit_list_from_analitic_composition_for_transport.append( collection_of_unit[row[df_productive_use]] )
                    input_proprietary_code_list_from_analitic_composition_for_transport.append( collection_of_code_and_description[row[df_code]][0] )
                except:
                    break

        for index, code in enumerate(input_code_list_from_analitic_composition_for_equipment):
            input_item_bulk_create_list_for_equipment.append( EquipmentItem(
                composition = composition_list_from_analitic_composition_for_equipment[index],
                generic_item = input_code_list_from_analitic_composition_for_equipment[index],
                generic_description = input_description_list_from_analitic_composition_for_equipment[index],
                input_group = input_group_list_from_analitic_composition_for_equipment[index],
                input_quantity = input_quantity_list_from_analitic_composition_for_equipment[index],
                input_use = input_productive_use_list_from_analitic_composition_for_equipment[index],
                unit = input_unit_list_from_analitic_composition_for_equipment[index],
                )
            )
        EquipmentItem.objects.bulk_create( input_item_bulk_create_list_for_equipment, ignore_conflicts=True )

        for index, code in enumerate(input_code_list_from_analitic_composition_for_workman):
            input_item_bulk_create_list_for_workman.append( WorkmanItem(
                composition = composition_list_from_analitic_composition_for_workman[index],
                generic_item = input_code_list_from_analitic_composition_for_workman[index],
                generic_description = input_description_list_from_analitic_composition_for_workman[index],
                input_group = input_group_list_from_analitic_composition_for_workman[index],
                input_quantity = input_quantity_list_from_analitic_composition_for_workman[index],
                unit = input_unit_list_from_analitic_composition_for_workman[index],
                )
            )
        WorkmanItem.objects.bulk_create( input_item_bulk_create_list_for_workman, ignore_conflicts=True )

        for index, code in enumerate(input_code_list_from_analitic_composition_for_material):
            input_item_bulk_create_list_for_material.append( MaterialItem(
                composition = composition_list_from_analitic_composition_for_material[index],
                generic_item = input_code_list_from_analitic_composition_for_material[index],
                generic_description = input_description_list_from_analitic_composition_for_material[index],
                input_group = input_group_list_from_analitic_composition_for_material[index],
                input_quantity = input_quantity_list_from_analitic_composition_for_material[index],
                unit = input_unit_list_from_analitic_composition_for_material[index],
                )
            )
        MaterialItem.objects.bulk_create( input_item_bulk_create_list_for_material, ignore_conflicts=True )

        for index, code in enumerate(input_code_list_from_analitic_composition_for_activity):
            input_item_bulk_create_list_for_activity.append( AuxiliaryActivityItem(
                composition = composition_list_from_analitic_composition_for_activity[index],
                generic_item = input_code_list_from_analitic_composition_for_activity[index],
                generic_description = input_description_list_from_analitic_composition_for_activity[index],
                input_group = input_group_list_from_analitic_composition_for_activity[index],
                input_quantity = input_quantity_list_from_analitic_composition_for_activity[index],
                unit = input_unit_list_from_analitic_composition_for_activity[index],
                )
            )
        AuxiliaryActivityItem.objects.bulk_create( input_item_bulk_create_list_for_activity, ignore_conflicts=True )
        
        reset_queries()
        start_time = time.time()
        for index, code in enumerate(input_code_list_from_analitic_composition_for_transport):
            input_item_bulk_create_list_for_transport.append( TransportItem(
                composition = composition_list_from_analitic_composition_for_transport[index],
                generic_item = input_code_list_from_analitic_composition_for_transport[index],
                generic_description = input_description_list_from_analitic_composition_for_transport[index],
                input_group = input_group_list_from_analitic_composition_for_transport[index],
                input_quantity = input_quantity_list_from_analitic_composition_for_transport[index],
                unit = input_unit_list_from_analitic_composition_for_transport[index],
                proprietary_item = input_proprietary_code_list_from_analitic_composition_for_transport[index],
                )
            )
        TransportItem.objects.bulk_create( input_item_bulk_create_list_for_transport, ignore_conflicts=True )
        end_time = time.time()
        duration = (end_time - start_time)
        print(f'Executou um total de {len(connection.queries)} queries')
        print(f'Tempo de execução {round(duration, 3)} segundos')
        reset_queries()

    def get_collection_of_equipment_item(self, source_file):
    ###### retorno de coleção de instâncias Composition
        return EquipmentItem.objects.select_related('composition').filter(composition__source_files__data_base=source_file.data_base).in_bulk()

    def relate_many_to_many_equipment_item_with_source_file(self, inputs, source_file):
    ###### criação das instâncias de relacionamento manytomany entre EquipmentItem e SourceFile
        input_item_manytomany_with_source_file = []
        for input in inputs:
            input_item_manytomany_with_source_file.append(EquipmentItem.source_files.through(
                equipmentitem_id = input,
                sourcefile_id = source_file.pk,
                )
            )
        EquipmentItem.source_files.through.objects.bulk_create( input_item_manytomany_with_source_file, ignore_conflicts=True )

    def get_collection_of_workman_item(self, source_file):
    ###### retorno de coleção de instâncias Composition
        return WorkmanItem.objects.select_related('composition').filter(composition__source_files__data_base=source_file.data_base).in_bulk()

    def relate_many_to_many_workman_item_with_source_file(self, inputs, source_file):
    ###### criação das instâncias de relacionamento manytomany entre WorkmanItem e SourceFile
        input_item_manytomany_with_source_file = []
        for input in inputs:
            input_item_manytomany_with_source_file.append(WorkmanItem.source_files.through(
                workmanitem_id = input,
                sourcefile_id = source_file.pk,
                )
            )
        WorkmanItem.source_files.through.objects.bulk_create( input_item_manytomany_with_source_file, ignore_conflicts=True )

    def get_collection_of_material_item(self, source_file):
    ###### retorno de coleção de instâncias Composition
        return MaterialItem.objects.select_related('composition').filter(composition__source_files__data_base=source_file.data_base).in_bulk()

    def relate_many_to_many_material_item_with_source_file(self, inputs, source_file):
    ###### criação das instâncias de relacionamento manytomany entre MaterialItem e SourceFile
        input_item_manytomany_with_source_file = []
        for input in inputs:
            input_item_manytomany_with_source_file.append(MaterialItem.source_files.through(
                materialitem_id = input,
                sourcefile_id = source_file.pk,
                )
            )
        MaterialItem.source_files.through.objects.bulk_create( input_item_manytomany_with_source_file, ignore_conflicts=True )

    def get_collection_of_activity_item(self, source_file):
    ###### retorno de coleção de instâncias Composition
        return AuxiliaryActivityItem.objects.select_related('composition').filter(composition__source_files__data_base=source_file.data_base).in_bulk()

    def relate_many_to_many_activity_item_with_source_file(self, inputs, source_file):
    ###### criação das instâncias de relacionamento manytomany entre AuxiliaryActivityItem e SourceFile
        input_item_manytomany_with_source_file = []
        for input in inputs:
            input_item_manytomany_with_source_file.append(AuxiliaryActivityItem.source_files.through(
                auxiliaryactivityitem_id = input,
                sourcefile_id = source_file.pk,
                )
            )
        AuxiliaryActivityItem.source_files.through.objects.bulk_create( input_item_manytomany_with_source_file, ignore_conflicts=True )

    def get_collection_of_transport_item(self, source_file):
    ###### retorno de coleção de instâncias Composition
        return TransportItem.objects.select_related('composition').filter(composition__source_files__data_base=source_file.data_base).in_bulk()

    def relate_many_to_many_transport_item_with_source_file(self, inputs, source_file):
    ###### criação das instâncias de relacionamento manytomany entre TransportItem e SourceFile
        input_item_manytomany_with_source_file = []
        for input in inputs:
            input_item_manytomany_with_source_file.append(TransportItem.source_files.through(
                transportitem_id = input,
                sourcefile_id = source_file.pk,
                )
            )
        TransportItem.source_files.through.objects.bulk_create( input_item_manytomany_with_source_file, ignore_conflicts=True )

    def process_source_file(self, type_file, response, source_file):
        
        if type_file == ANALITICO:

            data_frame = self.get_prepared_data_frame(type_file, response, source_file)
            self.scrape_multiple_basic_data_from_analitic_composition(source_file, data_frame)
            compositions = self.get_collection_of_composition(source_file)
            self.relate_many_to_many_composition_with_source_file(compositions, source_file)

            self.scrape_multiple_input_data_from_analitic_composition(source_file, data_frame)

            equipments = self.get_collection_of_equipment_item(source_file)
            self.relate_many_to_many_equipment_item_with_source_file(equipments, source_file)

            workmen = self.get_collection_of_workman_item(source_file)
            self.relate_many_to_many_workman_item_with_source_file(workmen, source_file)

            materials = self.get_collection_of_material_item(source_file)
            self.relate_many_to_many_material_item_with_source_file(materials, source_file)

            activities = self.get_collection_of_activity_item(source_file)
            self.relate_many_to_many_activity_item_with_source_file(activities, source_file)

            transports = self.get_collection_of_transport_item(source_file)
            self.relate_many_to_many_transport_item_with_source_file(transports, source_file)

        else:
            data_frame = self.get_prepared_data_frame(type_file, response, source_file)
            self.get_or_create_instancies_of_unit(data_frame)
            collection_of_unit = self.get_collection_of_unit()
            self.create_instancies_of_generic_item(data_frame, type_file)
            self.create_instancies_of_generic_description(data_frame, type_file)
            collection_of_unrelated_items = self.get_collection_of_generic_item_unrelated()
            collection_of_unrelated_descriptions = self.get_collection_of_generic_description_unrelated()

            self.relate_many_to_many_generic_item_with_source_file(data_frame, collection_of_unrelated_items, source_file)
            self.relate_many_to_many_generic_description_with_source_file(data_frame, collection_of_unrelated_descriptions, source_file)

            collection_of_related_items = self.get_collection_of_generic_item_related_with_source_file(df_code, source_file)
            collection_of_related_descriptions = self.get_collection_of_generic_description_related_with_source_file(df_description, source_file)
            self.switch_monetary_value(collection_of_related_items, data_frame, type_file, source_file, collection_of_unit)

            self.relate_many_to_many_generic_description_with_generic_item(data_frame, collection_of_related_items, collection_of_related_descriptions)

