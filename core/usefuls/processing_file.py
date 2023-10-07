from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine

from scraper.settings import default_dburl, DATABASES, dburl

from core.models import SourceFile, Composition, InputItem, GenericItem, GenericDescription, Unit, CompositionStamp
from core.usefuls.choices import ANALITICO, SINTETICO, EQUIPAMENTO, MAODEOBRA, MATERIAL, AUXILIAR, TEMPO_FIXO, TRANSPORTE
from core.usefuls.pattern import *
from core.usefuls.regex_pattern import CompositionRegex


class FileProcessor:
    def __init__(self, selected_object: SourceFile, page_dict: dict, num_pages: int) -> None:
        self.page_dict = page_dict
        self.selected_object = selected_object
        self.switch_type_file( self.selected_object.type_file, num_pages )

    def extract_nominal_data_from_compositions(self, num_pages: int, regex: CompositionRegex, page_content: list) -> list:
        composition_bulk_create_list = []
        for page in range(num_pages):
            composition_object = CompositionStamp()
            list_of_inputs_of_composition = page_content[page]
            i = 0
            while i < 5:
                row = list_of_inputs_of_composition[i]
                if regex.switch_regex(FIC_REGEX, row) != None:
                    fic_str = regex.switch_regex(FIC_REGEX, row)
                    composition_object.fic = Decimal(fic_str.replace(".", "").replace(",", "."))
                elif regex.switch_regex(DATA_BASE_REGEX, row) != None:
                    prod_str = regex.switch_regex(PRODUCTION_REGEX, row)
                    composition_object.production = Decimal(prod_str.replace(".", "").replace(",", "."))
                    composition_object.unit = regex.switch_regex(UNIT_REGEX, row)
                elif regex.switch_regex(COMPOSITION_CODE_REGEX, row) != None:
                    composition_object.composition_code = regex.switch_regex(COMPOSITION_CODE_REGEX, row)
                i += 1

            composition_bulk_create_list.append(
                Composition(
                    composition_code=composition_object.composition_code,
                    fic=composition_object.fic,
                    production=composition_object.production,
                    source_file=self.selected_object,
                    main_composition_group=composition_object.composition_code[0:2],
                )
            )
        return Composition.objects.bulk_create(composition_bulk_create_list)

    def extract_inputs_from_compositions(self, num_pages: int, regex: CompositionRegex, page_dict: dict, list_of_composition_objects: list) -> None:
        input_bulk_create_list = []

        for page in range(num_pages):
            composition_object = CompositionStamp()
            list_of_inputs_of_composition = page_dict[ page ]
            i = 0

            while i < len(list_of_inputs_of_composition):
                row = list_of_inputs_of_composition[i]

                if regex.switch_regex( EQUIPEMENT_CODE_REGEX, row ) != None:
                    code = regex.switch_regex( EQUIPEMENT_CODE_REGEX, row )
                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=EQUIPAMENTO,
                        main_input_quantity=Decimal( regex.switch_regex( EQUIPEMENT_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=Decimal( regex.switch_regex( EQUIPEMENT_UTIL_REGEX, row ).replace(".","").replace(",",".") ),
                        transported_input_code=None,
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                elif regex.switch_regex( EQUIPEMENT_QUANT_REGEX_ALFA, row ) != None:
                    quantity_eq = Decimal( regex.switch_regex( EQUIPEMENT_QUANT_REGEX_ALFA, row ).replace(".","").replace(",",".") )
                    use_eq = Decimal( regex.switch_regex( EQUIPEMENT_UTIL_REGEX_ALFA, row ).replace(".","").replace(",",".") )
                
                elif regex.switch_regex( EQUIPEMENT_CODE_REGEX_BETA, row ) != None:
                    code_eq = regex.switch_regex( EQUIPEMENT_CODE_REGEX_BETA, row )
                    input_object = InputItem(
                        main_input_code=code_eq,
                        main_input_group=EQUIPAMENTO,
                        main_input_quantity=quantity_eq,
                        main_input_use=use_eq,
                        transported_input_code=None,
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                elif regex.switch_regex( FIXED_UNIT_REGEX, row ) != None:
                    code = regex.switch_regex( FIXED_CODE_REGEX, row )
                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=TEMPO_FIXO,
                        main_input_quantity=Decimal( regex.switch_regex( FIXED_MATERIAL_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=regex.switch_regex( FIXED_MATERIAL_CODE_REGEX, row ),
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                elif regex.switch_regex( TRANSPORTATION_UNIT_REGEX, row ) != None:
                    code = regex.switch_regex( TRANSPORTATION_PV_CODE_REGEX, row )
                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=TRANSPORTE,
                        main_input_quantity=Decimal( regex.switch_regex( TRANSPORTATION_MATERIAL_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=regex.switch_regex( TRANSPORTATION_MATERIAL_CODE_REGEX, row ),
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                    code = regex.switch_regex( TRANSPORTATION_RP_CODE_REGEX, row )
                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=TRANSPORTE,
                        main_input_quantity=Decimal( regex.switch_regex( TRANSPORTATION_MATERIAL_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=regex.switch_regex( TRANSPORTATION_MATERIAL_CODE_REGEX, row ),
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                    code = regex.switch_regex( TRANSPORTATION_LN_CODE_REGEX, row )
                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=TRANSPORTE,
                        main_input_quantity=Decimal( regex.switch_regex( TRANSPORTATION_MATERIAL_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=regex.switch_regex( TRANSPORTATION_MATERIAL_CODE_REGEX, row ),
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                elif regex.switch_regex( TRANSPORTATION_FE_CODE_REGEX_ALFA, row ) != None:
                    code = regex.switch_regex( TRANSPORTATION_FE_CODE_REGEX_ALFA, row )
                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=TRANSPORTE,
                        main_input_quantity=Decimal( regex.switch_regex( TRANSPORTATION_MATERIAL_QUANT_REGEX_ALFA, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=regex.switch_regex( TRANSPORTATION_MATERIAL_CODE_REGEX_ALFA, row ),
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                elif regex.switch_regex( GENERAL_INPUT_CODE_REGEX, row ) != None:
                    code = regex.switch_regex( GENERAL_INPUT_CODE_REGEX, row )

                    if regex.switch_regex( GENERAL_INPUT_CODE_REGEX, row )[0] == 'P':
                        group = MAODEOBRA
                    elif regex.switch_regex( GENERAL_INPUT_CODE_REGEX, row )[0] == 'M':
                        group = MATERIAL
                    else:
                        group = AUXILIAR

                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=group,
                        main_input_quantity=Decimal( regex.switch_regex( GENERAL_INPUT_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=None,
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                elif regex.switch_regex( GENERAL_INPUT_QUANT_REGEX_ALFA, row ) != None:
                    quantity = Decimal( regex.switch_regex( GENERAL_INPUT_QUANT_REGEX_ALFA, row ).replace(".","").replace(",",".") )

                elif regex.switch_regex( GENERAL_INPUT_CODE_REGEX_BETA, row ) != None:
                    code = regex.switch_regex( GENERAL_INPUT_CODE_REGEX_BETA, row )

                    if regex.switch_regex( GENERAL_INPUT_CODE_REGEX_BETA, row )[0] == 'P':
                        group = MAODEOBRA
                    elif regex.switch_regex( GENERAL_INPUT_CODE_REGEX_BETA, row )[0] == 'M':
                        group = MATERIAL
                    else:
                        group = AUXILIAR
                
                    input_object = InputItem(
                        main_input_code=code,
                        main_input_group=group,
                        main_input_quantity=quantity,
                        main_input_use=None,
                        transported_input_code=None,
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                elif regex.switch_regex( BREAK_REGEX, row ) != None:
                    i += 6 #dont parse lastest rows of inputs

                elif regex.switch_regex( LAST_REGEX, row ) != None:
                    composition_object.stop_flag = True

                i += 1
        result = InputItem.objects.bulk_create( input_bulk_create_list )

    def switch_type_file(self, type_file, num_pages):
        if type_file == ANALITICO:
            regex = CompositionRegex()

            list_of_composition_objects = self.extract_nominal_data_from_compositions( num_pages, regex, self.page_dict )

            self.extract_inputs_from_compositions( num_pages, regex, self.page_dict, list_of_composition_objects )

        elif type_file == SINTETICO:
            print('Sintético')
        elif type_file == EQUIPAMENTO:
            print('Equipamento') 
        elif type_file == MAODEOBRA:
            print('Mão de obra')   
        elif type_file == MATERIAL:
            print('Material')


class FileXlsxProcessor:

    def __init__(self, response: dict, type_file: str, source_file: SourceFile) -> None:
        self.switch_type_file( type_file=type_file, response=response, source_file=source_file )

    def switch_type_file(self, type_file, response, source_file):
        if type_file == ANALITICO:

            print("OK")

        elif type_file == SINTETICO:
            data_frame = pd.read_excel(response["Body"].read(), names=['code', 'description', 'unit', 'price'], converters={'code':str, 'description':str, 'unit':str, 'price':float}, skiprows=source_file.number_of_lines_to_skip)
            
            generic_group_bulk_create_list = []
            description_bulk_create_list = []
            in_bulk_list = []

            list_object_generic_item = []
            list_object_generic_description = []
            
            generic_item_manytomany = []
            generic_description_manytomany = []

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


            for index, row in data_frame.iterrows():

                generic_description = GenericDescription.objects.get(description=row["description"])
                list_object_generic_description.append( generic_description.pk )
                
            
            items = GenericItem.objects.in_bulk( list_object_generic_item )
            descriptions = GenericDescription.objects.in_bulk( list_object_generic_description )

            for description in descriptions:

                generic_description_manytomany.append(GenericDescription.source_files.through(
                    genericdescription_id = description,
                    sourcefile_id = source_file.pk,
                    )
                )

            result_manytomany_description_created = GenericDescription.source_files.through.objects.bulk_create( generic_description_manytomany, ignore_conflicts=True )

            for item in items:

                generic_item_manytomany.append(GenericItem.source_files.through(
                    genericitem_id = item,
                    sourcefile_id = source_file.pk,
                    )
                )

            result_manytomany_item_created = GenericItem.source_files.through.objects.bulk_create( generic_item_manytomany, ignore_conflicts=True )



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