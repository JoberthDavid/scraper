from decimal import Decimal

from core.models import ModelFileCost, ModelComposition, ModelInput, CompositionStamp
from core.usefuls.choices import ANALITICO, SINTETICO, EQUIPAMENTO, MAODEOBRA, MATERIAL, AUXILIAR, TEMPO_FIXO, TRANSPORTE
from core.usefuls.pattern import *
from core.usefuls.regex_pattern import CompositionRegex


class FileProcessor:
    def __init__(self, selected_object: ModelFileCost, page_dict: dict, num_pages: int) -> None:
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
                ModelComposition(
                    composition_code=composition_object.composition_code,
                    fic=composition_object.fic,
                    production=composition_object.production,
                    file_cost=self.selected_object,
                    main_composition_group=composition_object.composition_code[0:2],
                )
            )
        return ModelComposition.objects.bulk_create(composition_bulk_create_list)

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
                    input_object = ModelInput(
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
                    input_object = ModelInput(
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
                    input_object = ModelInput(
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
                    input_object = ModelInput(
                        main_input_code=code,
                        main_input_group=TRANSPORTE,
                        main_input_quantity=Decimal( regex.switch_regex( TRANSPORTATION_MATERIAL_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=regex.switch_regex( TRANSPORTATION_MATERIAL_CODE_REGEX, row ),
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                    code = regex.switch_regex( TRANSPORTATION_RP_CODE_REGEX, row )
                    input_object = ModelInput(
                        main_input_code=code,
                        main_input_group=TRANSPORTE,
                        main_input_quantity=Decimal( regex.switch_regex( TRANSPORTATION_MATERIAL_QUANT_REGEX, row ).replace(".","").replace(",",".") ),
                        main_input_use=None,
                        transported_input_code=regex.switch_regex( TRANSPORTATION_MATERIAL_CODE_REGEX, row ),
                        related_composition=list_of_composition_objects[page],
                    )
                    input_bulk_create_list.append( input_object )

                    code = regex.switch_regex( TRANSPORTATION_LN_CODE_REGEX, row )
                    input_object = ModelInput(
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
                    input_object = ModelInput(
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

                    input_object = ModelInput(
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
                
                    input_object = ModelInput(
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
        result = ModelInput.objects.bulk_create( input_bulk_create_list )

    def switch_type_file(self, case, num_pages):
        if case == ANALITICO:
            regex = CompositionRegex()

            list_of_composition_objects = self.extract_nominal_data_from_compositions( num_pages, regex, self.page_dict )

            self.extract_inputs_from_compositions( num_pages, regex, self.page_dict, list_of_composition_objects )

        elif case == SINTETICO:
            print('Sintético')
        elif case == EQUIPAMENTO:
            print('Equipamento') 
        elif case == MAODEOBRA:
            print('Mão de obra')   
        elif case == MATERIAL:
            print('Material')