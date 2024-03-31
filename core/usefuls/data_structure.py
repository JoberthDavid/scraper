from core.models import *


class CompositionPreparer:

    def __init__(self) -> None:
        self.code_list = []
        self.description_list = []
        self.production_list = []
        self.unit_list = []
        self.fic_list = []
        self.group_list = []
        self.bulk_create_list = []

    def append_code(self, code: str) -> None:
        self.code_list.append(code)

    def append_description(self, description: str) -> None:
        self.description_list.append(description)

    def append_production(self, production: float) -> None:
        self.production_list.append(production)

    def append_unit(self, unit: str) -> None:
        self.unit_list.append(unit)

    def append_fic(self, fic: float) -> None:
        self.fic_list.append(fic)

    def append_group(self, group: str) -> None:
        self.group_list.append(group)

    def get_bulk_create_list(self) -> list:
        for index, code in enumerate(self.code_list):
            self.bulk_create_list.append( Composition(
                generic_item = self.code_list[index],
                generic_description = self.description_list[index],
                unit = self.unit_list[index],
                fic = self.fic_list[index],
                production = self.production_list[index],
                composition_group = self.group_list[index],
                )
            )
        return self.bulk_create_list


class InputEquipmentPreparer:

    def __init__(self) -> None:
        self.composition_list = []
        self.input_code_list = []
        self.input_description_list = []
        self.input_group_list = []
        self.input_quantity_list = []
        self.input_productive_use_list = []
        self.input_unit_list = []
        self.input_file_list = []
        self.bulk_create_list = []

    def append_input(self, composition: Composition, code: GenericItem, description: GenericDescription, group: str, quantity: float, use: float, unit: Unit, file: SourceFile) -> None:
        self.composition_list.append( composition )
        self.input_code_list.append( code )
        self.input_description_list.append( description )
        self.input_group_list.append( group )
        self.input_quantity_list.append( quantity )
        self.input_productive_use_list.append( use )
        self.input_unit_list.append( unit )
        self.input_file_list.append( file )

    def get_bulk_create_list(self) -> list:
        for index, code in enumerate(self.input_code_list):
            self.bulk_create_list.append( EquipmentItem(
                composition = self.composition_list[index],
                generic_item = self.input_code_list[index],
                generic_description = self.input_description_list[index],
                input_group = self.input_group_list[index],
                input_quantity = self.input_quantity_list[index],
                input_use = self.input_productive_use_list[index],
                unit = self.input_unit_list[index],
                )
            )
        return EquipmentItem.objects.bulk_create( self.bulk_create_list, ignore_conflicts=True )
    
    def relate_with_source_file(self, equipments) -> None:
        equipments_with_source_file = []
        for index, equipment in enumerate(equipments):
            equipments_with_source_file.append(EquipmentItem.source_files.through(
                equipmentitem_id = equipment.pk,
                sourcefile_id = self.input_file_list[index].pk,
                )
            )
        return EquipmentItem.source_files.through.objects.bulk_create( equipments_with_source_file, ignore_conflicts=True )

    def create_instances(self) -> None:
        equipments = self.get_bulk_create_list()
        self.relate_with_source_file(equipments)
        

class InputGenericPreparer:

    def __init__(self) -> None:
        self.composition_list = []
        self.input_code_list = []
        self.input_description_list = []
        self.input_group_list = []
        self.input_quantity_list = []
        self.input_unit_list = []
        self.input_file_list = []
        self.bulk_create_list = []

    def append_input(self, composition: Composition, code: GenericItem, description: GenericDescription, group: str, quantity: float, unit: Unit, file: SourceFile) -> None:
        self.composition_list.append( composition )
        self.input_code_list.append( code )
        self.input_description_list.append( description )
        self.input_group_list.append( group )
        self.input_quantity_list.append( quantity )
        self.input_unit_list.append( unit )
        self.input_file_list.append( file )


class InputWorkmanPreparer(InputGenericPreparer):


    def get_bulk_create_list(self) -> list:
        for index, code in enumerate(self.input_code_list):
            self.bulk_create_list.append( WorkmanItem(
                composition = self.composition_list[index],
                generic_item = self.input_code_list[index],
                generic_description = self.input_description_list[index],
                input_group = self.input_group_list[index],
                input_quantity = self.input_quantity_list[index],
                unit = self.input_unit_list[index],
                )
            )
        return WorkmanItem.objects.bulk_create( self.bulk_create_list, ignore_conflicts=True )


    def relate_with_source_file(self, workmen) -> None:
        workmen_with_source_file = []
        for index, workman in enumerate(workmen):
            workmen_with_source_file.append(WorkmanItem.source_files.through(
                workmanitem_id = workman.pk,
                sourcefile_id = self.input_file_list[index].pk,
                )
            )
        return WorkmanItem.source_files.through.objects.bulk_create( workmen_with_source_file, ignore_conflicts=True )

    def create_instances(self) -> None:
        workmen = self.get_bulk_create_list()
        self.relate_with_source_file(workmen)


class InputMaterialPreparer(InputGenericPreparer):
    

    def get_bulk_create_list(self) -> list:
        for index, code in enumerate(self.input_code_list):
            self.bulk_create_list.append( MaterialItem(
                composition = self.composition_list[index],
                generic_item = self.input_code_list[index],
                generic_description = self.input_description_list[index],
                input_group = self.input_group_list[index],
                input_quantity = self.input_quantity_list[index],
                unit = self.input_unit_list[index],
                )
            )
        return MaterialItem.objects.bulk_create( self.bulk_create_list, ignore_conflicts=True )

    def relate_with_source_file(self, materials) -> None:
        materials_with_source_file = []
        for index, material in enumerate(materials):
            materials_with_source_file.append(MaterialItem.source_files.through(
                materialitem_id = material.pk,
                sourcefile_id = self.input_file_list[index].pk,
                )
            )
        return MaterialItem.source_files.through.objects.bulk_create( materials_with_source_file, ignore_conflicts=True )

    def create_instances(self) -> None:
        materials = self.get_bulk_create_list()
        self.relate_with_source_file(materials)


class InputAuxiliaryActivityPreparer(InputGenericPreparer):
    

    def get_bulk_create_list(self) -> list:
        for index, code in enumerate(self.input_code_list):
            self.bulk_create_list.append( AuxiliaryActivityItem(
                composition = self.composition_list[index],
                generic_item = self.input_code_list[index],
                generic_description = self.input_description_list[index],
                input_group = self.input_group_list[index],
                input_quantity = self.input_quantity_list[index],
                unit = self.input_unit_list[index],
                )
            )
        return AuxiliaryActivityItem.objects.bulk_create( self.bulk_create_list, ignore_conflicts=True )

    def relate_with_source_file(self, auxiliaryactivities) -> None:
        auxiliaryactivities_with_source_file = []
        for index, auxiliaryactivity in enumerate(auxiliaryactivities):
            auxiliaryactivities_with_source_file.append(AuxiliaryActivityItem.source_files.through(
                auxiliaryactivityitem_id = auxiliaryactivity.pk,
                sourcefile_id = self.input_file_list[index].pk,
                )
            )
        return AuxiliaryActivityItem.source_files.through.objects.bulk_create( auxiliaryactivities_with_source_file, ignore_conflicts=True )

    def create_instances(self) -> None:
        auxiliaryactivities = self.get_bulk_create_list()
        self.relate_with_source_file(auxiliaryactivities)


class InputTransportPreparer(InputGenericPreparer):
    
    def __init__(self) -> None:
        self.composition_list = []
        self.input_code_list = []
        self.input_description_list = []
        self.input_group_list = []
        self.input_quantity_list = []
        self.input_unit_list = []
        self.input_proprietary_list = []
        self.input_file_list = []
        self.bulk_create_list = []

    def append_input(self, composition: Composition, code: GenericItem, description: GenericDescription, group: str, quantity: float, unit: Unit, proprietary: GenericItem, file: SourceFile) -> None:
        self.composition_list.append( composition )
        self.input_code_list.append( code )
        self.input_description_list.append( description )
        self.input_group_list.append( group )
        self.input_quantity_list.append( quantity )
        self.input_unit_list.append( unit )
        self.input_proprietary_list.append( proprietary )
        self.input_file_list.append( file )

    def get_bulk_create_list(self) -> list:
        for index, code in enumerate(self.input_code_list):
            self.bulk_create_list.append( TransportItem(
                composition = self.composition_list[index],
                generic_item = self.input_code_list[index],
                generic_description = self.input_description_list[index],
                input_group = self.input_group_list[index],
                input_quantity = self.input_quantity_list[index],
                unit = self.input_unit_list[index],
                proprietary_item = self.input_proprietary_list[index],
                )
            )
        return TransportItem.objects.bulk_create( self.bulk_create_list, ignore_conflicts=True )

    def relate_with_source_file(self, transports) -> None:
        transports_with_source_file = []
        for index, transport in enumerate(transports):
            transports_with_source_file.append(TransportItem.source_files.through(
                transportitem_id = transport.pk,
                sourcefile_id = self.input_file_list[index].pk,
                )
            )
        return TransportItem.source_files.through.objects.bulk_create( transports_with_source_file, ignore_conflicts=True )

    def create_instances(self) -> None:
        transports = self.get_bulk_create_list()
        self.relate_with_source_file(transports)