from typing import Any
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from core.models import SourceFile, Unit, Composition, EquipmentItem, WorkmanItem, MaterialItem, AuxiliaryActivityItem, TransportItem, GenericItem, GenericDescription, MonetaryValue

from django.contrib import messages
from django.utils.translation import ngettext

from core.tasks import process_file_in_background

from core.usefuls.choices import *


admin.site.site_header = "SICRO"
admin.site.index_title = "API custos"
admin.site.site_title = "Administração"


class SourceFileAdmin(admin.ModelAdmin):

    list_display = [ str, 'status']
    order_by = 'data_base'
    date_hierarchy = 'data_base'
    actions = ['process_file',]

    def select_object(self, queryset: QuerySet) -> SourceFile:
        return queryset.filter(status=False).first()
            
    def success_message_about_file_processing( self, request: HttpRequest, queryset: QuerySet) -> None:
        self.message_user( 
            request, 
            ngettext(
                "O arquivo selecionado está em processamento.",
                "Apenas um arquivo está em processamento de todos os selecionados.",
                len(queryset),
                ),
                messages.INFO )

    def warning_message_about_file_processing( self, request: HttpRequest, queryset: QuerySet) -> None:
        self.message_user( 
            request, 
            ngettext(
                "O arquivo selecionado não foi processado.",
                "Os arquivos selecionados não foram processados.", 
                len(queryset),
                ),
                messages.WARNING )

    @admin.action(description='Processar arquivo')
    def process_file(self, request: HttpRequest, queryset: QuerySet) -> None:
        selected_object = self.select_object(queryset)

        if selected_object is None:
            self.message_user(
                request,
                "Nenhum arquivo pendente foi encontrado para processamento.",
                messages.WARNING,
            )
            return

        try:
            process_file_in_background.delay(selected_object.id)

            self.success_message_about_file_processing(
                request,
                queryset,
            )

        except Exception as error:
            self.message_user(
                request,
                f"Erro ao enviar o arquivo para processamento: {error}",
                messages.ERROR,
            )


class UnitAdmin(admin.ModelAdmin):

    order_by = ['unit',]
    list_filter = ['dimensional',]

class CompositionAdmin(admin.ModelAdmin):

    order_by = ['composition_group','source_files',]
    list_filter = ['composition_group',]
    search_fields = ['generic_item__code', 'generic_description__description']


class EquipmentItemAdmin(admin.ModelAdmin):
    
    search_fields = ['composition__generic_item__code', 'generic_description__description',]
    list_filter = [ 'source_files', ]
    

class WorkmanItemAdmin(admin.ModelAdmin):

    search_fields = ['composition__generic_item__code', 'generic_description__description',]
    list_filter = [ 'source_files', ]


class MaterialItemAdmin(admin.ModelAdmin):

    search_fields = ['composition__generic_item__code', 'generic_description__description',]
    list_filter = [ 'source_files', ]


class AuxiliaryActivitytemAdmin(admin.ModelAdmin):

    search_fields = ['composition__generic_item__code', 'generic_description__description',]
    list_filter = [ 'source_files', ]


class TransportItemAdmin(admin.ModelAdmin):

    search_fields = ['composition__generic_item__code', 'generic_description__description', 'input_group']
    list_filter = [ 'source_files', 'input_group']


class GenericItemAdmin(admin.ModelAdmin):

    order_by = 'code'
    list_display = [ 'code',]
    search_fields = ['code',]
    list_filter = [ 'source_files', ]


class GenericDescriptionAdmin(admin.ModelAdmin):

    order_by = 'generic_items'
    list_display = [ 'description' ]
    search_fields = [ 'generic_items__code', 'description',]
    list_filter = [ 'source_files',]


class MonetaryValueAdmin(admin.ModelAdmin):

    order_by = 'generic_item'
    list_display = [ 'generic_item', 'monetary_value', 'unit','type_system']
    search_fields = [ 'generic_item__code',]
    list_filter = [ 'type_system', 'classification', 'source_file', 'unit__dimensional']


admin.site.register(MonetaryValue, MonetaryValueAdmin)
admin.site.register(GenericDescription, GenericDescriptionAdmin)
admin.site.register(GenericItem, GenericItemAdmin)
admin.site.register(SourceFile, SourceFileAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Composition, CompositionAdmin)
admin.site.register(EquipmentItem, EquipmentItemAdmin)
admin.site.register(WorkmanItem, WorkmanItemAdmin)
admin.site.register(MaterialItem, MaterialItemAdmin)
admin.site.register(AuxiliaryActivityItem, AuxiliaryActivitytemAdmin)
admin.site.register(TransportItem, TransportItemAdmin)