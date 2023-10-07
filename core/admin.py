from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from core.models import SourceFile, Composition, InputItem, GenericItem, GenericDescription

from django.contrib import messages
from django.utils.translation import ngettext

from core.tasks import process_file_in_background


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
        try:
            selected_object = self.select_object( queryset )

            process_file_in_background.delay( selected_object.id )

            self.success_message_about_file_processing( request, queryset )

        except:
            self.warning_message_about_file_processing( request, queryset )
            

class CompositionAdmin(admin.ModelAdmin):

    order_by = 'source_file'
    list_filter = ['source_file','main_composition_group',]
    search_fields = ['composition_code']


class InputItemAdmin(admin.ModelAdmin):

    order_by = 'related_composition'
    list_filter = ['related_composition__source_file','main_input_group','related_composition__main_composition_group',]
    search_fields = ['related_composition__composition_code',]


class GenericItemAdmin(admin.ModelAdmin):

    order_by = 'code'
    list_display = [ 'code', 'unit']
    search_fields = ['code',]
    list_filter = [ 'source_files', 'unit', 'group',]


class GenericDescriptionAdmin(admin.ModelAdmin):

    order_by = 'generic_item'
    list_display = [ 'generic_item', 'description' ]
    search_fields = [ 'description',]
    list_filter = [ 'source_files',]


admin.site.register(GenericDescription, GenericDescriptionAdmin)
admin.site.register(GenericItem, GenericItemAdmin)
admin.site.register(SourceFile, SourceFileAdmin)
admin.site.register(Composition, CompositionAdmin)
admin.site.register(InputItem, InputItemAdmin)