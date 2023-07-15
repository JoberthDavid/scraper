from decimal import Decimal
import datetime
from django.db import models
from django.core.validators import FileExtensionValidator

from core.usefuls.choices import *


class ModelFileCost(models.Model):

    methodology = models.CharField(
        verbose_name="Metodologia",
        max_length=2,
        choices=METHODOLOGY,
        default=SICRO,
        )
    data_base = models.DateField(
        verbose_name="Data-base",
        auto_now=False, auto_now_add=False
        )
    file = models.FileField(
        verbose_name="Arquivo PDF",
        upload_to='core/pdf_uploaded/',
        validators=[FileExtensionValidator(['pdf'])]
        )
    uf = models.CharField(
        verbose_name="UF",
        max_length=2,
        choices=UF,
        default=GOIAS,        
        )
    type_system = models.CharField(
        verbose_name="Tipo de sistema",
        max_length=2,
        choices=TYPE_SYSTEM,
        default=ONERADO,
        )
    type_file = models.CharField(
        verbose_name="Tipo de arquivo",
        max_length=2,
        choices=FILE,
        default=ANALITICO,
        )
    status = models.BooleanField(
        verbose_name="Arquivo processado",
        default=False,
    )


    class Meta:
        verbose_name="Arquivo de custo"
        verbose_name_plural="Arquivos de custos"

    def __str__(self):
        return " - ".join([self.methodology, self.uf, self.parser_data_base_to_string(), self.type_system, self.type_file])
    
    def format_data_base(self):
        return self.data_base.__format__("%m/%Y")

    def parser_data_base_to_string(self):
        return str(self.format_data_base())

    def get_absolute_url(self):
        return '/scraper/%i/' % self.pk
    

class ModelComposition(models.Model):

    composition_code = models.CharField(
        verbose_name="Código",
        max_length=10,
        )
    fic = models.DecimalField(
        verbose_name="FIC",
        max_digits=18,
        decimal_places=5,
        default=Decimal(0.0),
        )
    production = models.DecimalField(
        verbose_name="Produção",
        max_digits=18,
        decimal_places=5
        )
    file_cost = models.ForeignKey(
        ModelFileCost,
        verbose_name='Arquivo relacionado',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )
    main_composition_group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=COMPOSITION_GROUP,
        )
    status = models.BooleanField(
        verbose_name="Composição validada",
        default=False,
    )

    class Meta:
        verbose_name="Composição"
        verbose_name_plural="Composições"

    def __str__(self):
        return str(self.composition_code)
    
    def update_group(self):
        self.main_composition_group = self.__str__()[0:2]
        self.save()


class ModelInput(models.Model):

    main_input_code = models.CharField(
        verbose_name="Código",
        max_length=10,
        )
    main_input_group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=INPUT_GROUP,
        )
    main_input_quantity = models.DecimalField(
        verbose_name="Quantidade",
        max_digits=18,
        decimal_places=5,
        )
    main_input_use = models.DecimalField(
        verbose_name="Utilização",
        max_digits=18,
        decimal_places=5,
        default=None,
        null=True,
        blank=True,
        )
    transported_input_code = models.CharField(
        verbose_name="Código insumo transportado",
        max_length=10,
        default=None,
        null=True,
        blank=True,

        )
    related_composition = models.ForeignKey(
        ModelComposition,
        verbose_name='Composição relacionada',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )

    class Meta:
        verbose_name="Apropriação"
        verbose_name_plural="Apropriações"

    def __str__(self):
        return str(self.related_composition) + " - " + str(self.main_input_code)


class CompositionStamp:

    def __init__( self ) -> None:
        self.fic = Decimal(0.0)
        self.data_base = datetime.date(1900,1,1)
        self.production = Decimal(0.0)
        self.unit = ''
        self.composition_code = ''       
        self.stop_flag = False