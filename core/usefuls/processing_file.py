from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine

from scraper.settings import default_dburl, DATABASES, dburl

from core.usefuls.data_structure import *
from core.models import *
from core.usefuls.choices import *
import re

from django.db.models import Prefetch


class FileXlsxPreparer:

    def get_data_frame_prepared(self, response: dict, type_file: str, source_file: SourceFile) -> pd.core.frame.DataFrame:
        if type_file == ANALITICO:
            data_frame = pd.read_excel(response[df_body].read(), names=[df_code, df_description, df_quantity, df_productive_use, df_unproductive_use, df_productive_cost, df_unproductive_cost, df_production, df_unit] )#, converters={df_code:str, df_description:str, df_quantity:str, df_productive_use:str, df_unproductive_use:str, df_productive_cost:str, df_unproductive_cost:str, df_production:str, df_unit:str} )
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


class UnitPreparer:

    def __init__(self, data_frame: pd.core.frame.DataFrame ) -> None:
        self.get_or_create_instancies_of_unit( data_frame=data_frame )

    def get_or_create_instancies_of_unit(self, data_frame: pd.core.frame.DataFrame) -> None:
    ###### criação das instâncias Unit
        for index, row in data_frame.iterrows():
            object, created = Unit.objects.get_or_create(
                unit=row[df_unit],
                dimensional=None,
            )

    @classmethod
    def get_collection_of_unit(self) -> dict:
    ###### retorno de coleção de instâncias Unit
        return Unit.objects.all().in_bulk( field_name=df_unit )


class MonetaryValuePreparer:

    def __init__(self, data_frame: pd.core.frame.DataFrame, type_file: str, source_file: SourceFile, related_items: dict, units: dict):
        self.switch_monetary_value(data_frame=data_frame, type_file=type_file, source_file=source_file, related_items=related_items, units=units)

    def create_instancies_of_monetary_value(self, data_frame: pd.core.frame.DataFrame, type_file: str, source_file: SourceFile, related_items: dict, units: dict, classification: str, monetary_value: str):
    ###### criação das instâncias MonetaryValue
        monetary_value_bulk_create_list = []
        if type_file == SINTETICO:
            group = COMPOSICAO
        else:
            group = type_file
        for index, row in data_frame.iterrows():
            monetary_value_bulk_create_list.append( MonetaryValue(
                generic_item = related_items[row[df_code]],
                source_file = source_file,
                unit = units[row[df_unit]],
                monetary_value = row[monetary_value],
                classification = classification,
                group = group,
                type_system = source_file.type_system,
                )
            )
        MonetaryValue.objects.bulk_create( monetary_value_bulk_create_list, ignore_conflicts=True )

    def switch_monetary_value(self, data_frame: pd.core.frame.DataFrame, type_file: str, source_file: SourceFile, related_items: dict, units: dict):
        if type_file == SINTETICO:
            self.create_instancies_of_monetary_value(data_frame=data_frame, type_file=COMPOSICAO, source_file=source_file, related_items=related_items, units=units, classification=PRECO, monetary_value=df_monetary_value)
        elif type_file == EQUIPAMENTO:
            self.create_instancies_of_monetary_value(data_frame=data_frame, type_file=type_file, source_file=source_file, related_items=related_items, units=units, classification=PRODUTIVO, monetary_value=df_productive_cost)
            self.create_instancies_of_monetary_value(data_frame=data_frame, type_file=type_file, source_file=source_file, related_items=related_items, units=units, classification=IMPRODUTIVO, monetary_value=df_unproductive_cost)
        elif type_file == MAODEOBRA or type_file == MATERIAL:
            self.create_instancies_of_monetary_value(data_frame=data_frame, type_file=type_file, source_file=source_file, related_items=related_items, units=units, classification=CUSTO, monetary_value=df_monetary_value)


class GenericItemPreparer:

    def __init__(self, data_frame: pd.core.frame.DataFrame) -> None:
        self.create_instancies_of_generic_item(data_frame=data_frame)

    def create_instancies_of_generic_item(self, data_frame: pd.core.frame.DataFrame) -> None:
    ###### criação das instâncias GenericItem
        generic_item_bulk_create_list = []
        for index, row in data_frame.iterrows():
            generic_item_bulk_create_list.append( GenericItem(
                code = row[df_code],
                )
            )
        GenericItem.objects.bulk_create( generic_item_bulk_create_list, ignore_conflicts=True )

    def get_collection_of_generic_item_unrelated(self) -> dict:
    ###### retorno de coleção de instâncias GenericItem sem relacionamentos construídos
        return GenericItem.objects.in_bulk(field_name='code')


class GenericDescriptionPreparer:

    def __init__(self, data_frame: pd.core.frame.DataFrame, type_file) -> None:
        self.create_instancies_of_generic_description(data_frame=data_frame, type_file=type_file)

    def create_instancies_of_generic_description(self, data_frame: pd.core.frame.DataFrame, type_file) -> None:
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

    def get_collection_of_generic_description_unrelated(self) -> dict:
    ###### retorno de coleção de instâncias GenericDescription sem relacionamentos construídos
        return GenericDescription.objects.in_bulk(field_name='description')


class SourceFilePreparer:

    def __init__(self, data_frame: pd.core.frame.DataFrame, unrelated_items: dict, unrelated_descriptions: dict, source_file: SourceFile) -> None:
        self.relate_many_to_many_generic_item_with_source_file(data_frame=data_frame, unrelated_items=unrelated_items, source_file=source_file)
        self.relate_many_to_many_generic_description_with_source_file(data_frame=data_frame, unrelated_descriptions=unrelated_descriptions, source_file=source_file)
        related_items = self.get_collection_of_generic_item_related_with_source_file(field=df_code, source_file=source_file)
        related_descriptions = self.get_collection_of_generic_description_related_with_source_file(field=df_description, source_file=source_file)
        self.relate_many_to_many_generic_description_with_generic_item(data_frame=data_frame, related_items=related_items, related_descriptions=related_descriptions)

    def relate_many_to_many_generic_item_with_source_file(self, data_frame: pd.core.frame.DataFrame, unrelated_items: dict, source_file: SourceFile) -> None:
    ###### criação das instâncias de relacionamento manytomany entre GenericItem e SourceFile
        generic_item_manytomany = []
        for index, row in data_frame.iterrows():
            generic_item_manytomany.append(GenericItem.source_files.through(
                genericitem_id = unrelated_items[ row[df_code] ].pk,
                sourcefile_id = source_file.pk,
                )
            )
        GenericItem.source_files.through.objects.bulk_create( generic_item_manytomany, ignore_conflicts=True )

    def relate_many_to_many_generic_description_with_source_file(self, data_frame: pd.core.frame.DataFrame, unrelated_descriptions: dict, source_file: SourceFile) -> None:
    ###### criação das instâncias de relacionamento manytomany entre GenericDescription e SourceFile
        generic_description_manytomany_with_source_file = []
        for index, row in data_frame.iterrows():
            generic_description_manytomany_with_source_file.append(GenericDescription.source_files.through(
                genericdescription_id = unrelated_descriptions[ row[df_description] ].pk,
                sourcefile_id = source_file.pk,
                )
            )
        GenericDescription.source_files.through.objects.bulk_create( generic_description_manytomany_with_source_file, ignore_conflicts=True )

    def relate_many_to_many_generic_description_with_generic_item(self, data_frame: pd.core.frame.DataFrame, related_items: dict, related_descriptions: dict) -> None:
    ###### criação das instâncias de relacionamento manytomany entre GenericDescription e GenericItem
        generic_description_manytomany_with_generic_item = []
        for index, row in data_frame.iterrows():
            generic_description_manytomany_with_generic_item.append(GenericDescription.generic_items.through(
                genericdescription_id = related_descriptions[ row[df_description] ].pk,
                genericitem_id = related_items[ row[df_code] ].pk,
                )
            )
        GenericDescription.generic_items.through.objects.bulk_create( generic_description_manytomany_with_generic_item, ignore_conflicts=True )

    @classmethod
    def get_collection_of_generic_item_related_with_source_file(self, field: str, source_file: SourceFile, group=None) -> dict:
    ###### retorno de coleção de instâncias GenericItem
        if not(group):
            return GenericItem.objects.filter(source_files__data_base=source_file.data_base).in_bulk( field_name=field )
        elif group == COMPOSICAO:
            return GenericItem.objects.filter(source_files__data_base=source_file.data_base).filter(source_files__type_file=SINTETICO).in_bulk( field_name=field )
        else:
            return GenericItem.objects.filter(source_files__data_base=source_file.data_base).filter(source_files__type_file=group).in_bulk( field_name=field )

    @classmethod
    def get_collection_of_generic_description_related_with_source_file(self, field: str, source_file: SourceFile) -> dict:
    ###### retorno de coleção de instâncias GenericDescription
        return GenericDescription.objects.filter(source_files__data_base=source_file.data_base).in_bulk( field_name=field )        


class BasicDataCompositionPreparer:

    def __init__(self, data_frame: pd.core.frame.DataFrame, source_file: SourceFile) -> None:
        self.scrape_multiple_basic_data_from_analitic_composition(data_frame=data_frame, source_file=source_file)
        compositions = self.get_collection_of_composition(source_file=source_file)
        self.relate_many_to_many_composition_with_source_file(compositions=compositions,source_file=source_file)

    def scrape_multiple_basic_data_from_analitic_composition(self, data_frame: pd.core.frame.DataFrame, source_file: SourceFile) -> None:
        collection_of_unit = UnitPreparer.get_collection_of_unit()
        collection_of_generic_item = SourceFilePreparer.get_collection_of_generic_item_related_with_source_file(field=df_code, source_file=source_file, group=COMPOSICAO)
        collection_of_generic_description = SourceFilePreparer.get_collection_of_generic_description_related_with_source_file(field=df_description, source_file=source_file)
        composition_collection = CompositionPreparer()

        for index, row in data_frame.iterrows():
            if row[df_code] == "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS - SICRO":
                    composition_collection.append_fic( row[df_production] )
            elif row[df_code] == "Custo Unitário de Referência":
                    composition_collection.append_production( row[df_production] )
                    composition_collection.append_unit( collection_of_unit[row[df_unit]] )
            elif row[df_production] == "Valores em reais (R$)":
                    composition_collection.append_code( collection_of_generic_item[row[df_code]] )
                    composition_collection.append_description( collection_of_generic_description[row[df_description]] )
                    composition_collection.append_group( row[df_code][:2] )
        lista = composition_collection.get_bulk_create_list()

        return Composition.objects.bulk_create( lista, ignore_conflicts=True )

    def get_collection_of_composition(self, source_file: SourceFile) -> dict:
    ###### retorno de coleção de instâncias Composition
        return Composition.objects.select_related('generic_item').filter(generic_item__source_files__data_base=source_file.data_base).in_bulk()

    def relate_many_to_many_composition_with_source_file(self, compositions: dict, source_file: SourceFile) -> None:
    ###### criação das instâncias de relacionamento manytomany entre Composition e SourceFile
        composition_manytomany_with_source_file = []
        for composition in compositions:
            composition_manytomany_with_source_file.append(Composition.source_files.through(
                composition_id = composition,
                sourcefile_id = source_file.pk,
                )
            )
        return Composition.source_files.through.objects.bulk_create( composition_manytomany_with_source_file, ignore_conflicts=True )


class AllocationPreparer:

    def __init__(self, data_frame: pd.core.frame.DataFrame, source_file: SourceFile) -> None:
        self.scrape_multiple_input_data_from_analitic_composition( data_frame=data_frame, source_file=source_file )

    def scrape_multiple_input_data_from_analitic_composition(self, data_frame: pd.core.frame.DataFrame, source_file: SourceFile):
        collection_of_unit = UnitPreparer.get_collection_of_unit()
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

        equipments = InputEquipmentPreparer()
        workmen = InputWorkmanPreparer()
        materials = InputMaterialPreparer()
        auxiliary_activities = InputAuxiliaryActivityPreparer()
        transports = InputTransportPreparer()

        for index, row in data_frame.iterrows():
            if row[df_production] == "Valores em reais (R$)":
                composition = collection_of_composition[ row[df_code] ]
            elif re.match( r'[EA]\d{4}', str( row[df_code] ) ):
                equipments.append_input(composition=composition, code=collection_of_code_and_description[row[df_code]][0], description=collection_of_code_and_description[row[df_code]][1], group=EQUIPAMENTO, quantity=row[df_quantity], use=row[df_productive_use], unit=collection_of_unit["h"])
            elif re.match( r'[P]\d{4}', str( row[df_code] ) ):
                workmen.append_input(composition=composition, code=collection_of_code_and_description[row[df_code]][0], description=collection_of_code_and_description[row[df_code]][1], group=MAODEOBRA, quantity=row[df_quantity], unit=collection_of_unit[row[df_productive_use]])
            elif re.match( r'[M]\d{4}', str( row[df_code] ) ) and ( type( row[df_productive_use] ) == str ) and not( re.match( r'\d{7}', str( row[df_unproductive_use] ) ) ) and not( re.match( r'\d{7}', str( row[df_production] ) ) ) :
                materials.append_input(composition=composition, code=collection_of_code_and_description[row[df_code]][0], description=collection_of_code_and_description[row[df_code]][1], group=MATERIAL, quantity=row[df_quantity], unit=collection_of_unit[row[df_productive_use]])
            elif re.match( r'\d{7}', str( row[df_code] ) ) and ( type( row[df_productive_use] ) == str ) and not( re.match( r'\d{7}', str( row[df_unproductive_use] ) ) ) and not( re.match( r'\d{7}', str( row[df_production] ) ) ) :
                auxiliary_activities.append_input(composition=composition, code=collection_of_code_and_description[row[df_code]][0], description=collection_of_code_and_description[row[df_code]][1], group=AUXILIAR, quantity=row[df_quantity], unit=collection_of_unit[row[df_productive_use]])
            elif re.match( r'\d{7}', str( row[df_quantity] ) ):
                transports.append_input(composition=composition, code=collection_of_code_and_description[row[df_quantity]][0], description=collection_of_code_and_description[row[df_quantity]][1], group=TEMPO_FIXO, quantity=row[df_productive_use], unit=collection_of_unit[row[df_unproductive_use]], proprietary=collection_of_code_and_description[row[df_code]][0])
            elif re.match( r'\d{7}', str( row[df_unproductive_use] ) ) and re.match( r'\d{7}', str( row[df_productive_cost] ) ) and re.match( r'\d{7}', str( row[df_unproductive_cost] ) ):
                # first mean of transportation
                transports.append_input(composition=composition, code=collection_of_code_and_description[row[df_unproductive_use]][0], description=collection_of_code_and_description[row[df_unproductive_use]][1], group=LEITO_NATURAL, quantity=row[df_quantity], unit=collection_of_unit[row[df_productive_use]], proprietary=collection_of_code_and_description[row[df_code]][0])
                # second mean of transportation
                transports.append_input(composition=composition, code=collection_of_code_and_description[row[df_productive_cost]][0], description=collection_of_code_and_description[row[df_productive_cost]][1], group=REVESTIMENTO_PRIMARIO, quantity=row[df_quantity], unit=collection_of_unit[row[df_productive_use]], proprietary=collection_of_code_and_description[row[df_code]][0])
                # third mean of transportation
                transports.append_input(composition=composition, code=collection_of_code_and_description[row[df_unproductive_cost]][0], description=collection_of_code_and_description[row[df_unproductive_cost]][1], group=PAVIMENTADO, quantity=row[df_quantity], unit=collection_of_unit[row[df_productive_use]], proprietary=collection_of_code_and_description[row[df_code]][0])
            elif re.match( r'\d{7}', str( row[df_production] ) ) and ( type( row[df_productive_use] ) == str ):
                # fourth mean of transportation
                transports.append_input(composition=composition, code=collection_of_code_and_description[row[df_production]][0], description=collection_of_code_and_description[row[df_production]][1], group=FERROVIARIO, quantity=row[df_quantity], unit=collection_of_unit[row[df_productive_use]], proprietary=collection_of_code_and_description[row[df_code]][0])

        equipments.create_instances(source_file=source_file)
        workmen.create_instances(source_file=source_file)
        materials.create_instances(source_file=source_file)
        auxiliary_activities.create_instances(source_file=source_file)
        transports.create_instances(source_file=source_file)


class FileXlsxProcessor:

    def __init__(self, data_frame: pd.core.frame.DataFrame, type_file: str, source_file: SourceFile) -> None:
        self.process_source_file( data_frame=data_frame, type_file=type_file, source_file=source_file )

    def process_source_file(self, data_frame: pd.core.frame.DataFrame, type_file, source_file: SourceFile ) -> None:
        
        if type_file == ANALITICO:
            composition_preparer = BasicDataCompositionPreparer(data_frame=data_frame, source_file=source_file)
            allocation_preparer = AllocationPreparer(data_frame=data_frame, source_file=source_file)

        else:
            unit_preparer = UnitPreparer( data_frame=data_frame )
            collection_of_unit = unit_preparer.get_collection_of_unit()

            item_preparer = GenericItemPreparer(data_frame=data_frame)
            collection_of_unrelated_items = item_preparer.get_collection_of_generic_item_unrelated()

            description_preparer = GenericDescriptionPreparer(data_frame=data_frame, type_file=type_file)
            collection_of_unrelated_descriptions = description_preparer.get_collection_of_generic_description_unrelated()

            source_file_preparer = SourceFilePreparer(data_frame=data_frame, unrelated_items=collection_of_unrelated_items, unrelated_descriptions=collection_of_unrelated_descriptions, source_file=source_file)
            collection_of_related_items = source_file_preparer.get_collection_of_generic_item_related_with_source_file(field=df_code, source_file=source_file)

            monetary_preparer = MonetaryValuePreparer(data_frame=data_frame, type_file=type_file, source_file=source_file, related_items=collection_of_related_items, units=collection_of_unit)