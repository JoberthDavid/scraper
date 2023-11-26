from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from core.models import SourceFile, Composition, InputItem, GenericItem, GenericDescription, MonetaryValue

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

    order_by = ['composition_group','source_file',]
    list_filter = ['composition_group','source_file__data_base',]
    search_fields = ['generic_item__code', 'generic_description__description']


class InputItemAdmin(admin.ModelAdmin):

    search_fields = ['composition__source_file','generic_description__description',]


class GenericItemAdmin(admin.ModelAdmin):

    order_by = 'code'
    list_display = [ 'code',]
    search_fields = ['code',]
    list_filter = [ 'group', 'source_files', ]


class GenericDescriptionAdmin(admin.ModelAdmin):

    order_by = 'generic_items'
    list_display = [ 'description' ]
    search_fields = [ 'generic_items__code', 'description',]
    list_filter = [ 'source_files',]


class MonetaryValueAdmin(admin.ModelAdmin):

    order_by = 'generic_item'
    list_display = [ 'generic_item', 'monetary_value', 'unit']
    search_fields = [ 'generic_item__code',]
    list_filter = [ 'classification', 'source_file',]


admin.site.register(MonetaryValue, MonetaryValueAdmin)
admin.site.register(GenericDescription, GenericDescriptionAdmin)
admin.site.register(GenericItem, GenericItemAdmin)
admin.site.register(SourceFile, SourceFileAdmin)
admin.site.register(Composition, CompositionAdmin)
admin.site.register(InputItem, InputItemAdmin)