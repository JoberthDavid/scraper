from decimal import Decimal

from django.db import models
from django.core.validators import FileExtensionValidator

from core.usefuls.choices import *


class SourceFile(models.Model):

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
    source_file = models.FileField(
        verbose_name="Arquivo de origem",
        upload_to='core/file_uploaded/',
        validators=[FileExtensionValidator(['xlsx',])]
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
        default=NAO_APLICAVEL,
        )
    type_file = models.CharField(
        verbose_name="Tipo de arquivo",
        max_length=2,
        choices=FILE,
        default=ONERADO,
        )
    status = models.BooleanField(
        verbose_name="Arquivo processado",
        default=False,
    )
    number_of_lines_to_skip = models.IntegerField(
        verbose_name="Número de linhas de cabeçalho",
        blank=True,
        null=True,
        default=0,
    )

    class Meta:
        verbose_name="Arquivo de origem"
        verbose_name_plural="Arquivos de origem"
        constraints = [
            models.UniqueConstraint(
               fields=['methodology', 'data_base', 'type_system','type_file'],
               name="unique_file"
            )
        ]

    def __str__(self):
        return " - ".join([self.methodology, self.uf, self.parser_data_base_to_string(), self.type_system, self.type_file])
    
    def format_data_base(self):
        return self.data_base.__format__("%m/%Y")

    def parser_data_base_to_string(self):
        return str(self.format_data_base())

    def get_absolute_url(self):
        return '/scraper/%i/' % self.pk
    

class Unit(models.Model):

    #acrescentar um campo de dimensão
    unit = models.CharField(
        verbose_name="Unidade",
        max_length=10,
        default=None,
        )

    class Meta:
        verbose_name="Unidade"
        verbose_name_plural="Unidades"
        constraints = [
            models.UniqueConstraint(
               fields=['unit',],
               name="unique_unit"
            )
        ]

    def __str__(self):
        return str(self.unit)


class GenericItem(models.Model):
    
    code = models.CharField(
        verbose_name="Código",
        max_length=20,
        unique=True,
        blank=False,
        editable=False,
        )
    source_files = models.ManyToManyField(
        SourceFile,
        verbose_name='Arquivos de origem',
        related_name='items',
        default=None,
        blank=True,
        )
    group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=GENERIC_GROUP,
        default=None,
        )

    class Meta:
        verbose_name="Item genérico"
        verbose_name_plural="Itens genéricos"
        constraints = [
            models.UniqueConstraint(
               fields=['code',],
               name="unique_generic_item"
            )
        ]

    def __str__(self):
        return str(self.code)


class GenericDescription(models.Model):

    generic_items = models.ManyToManyField(
        GenericItem,
        verbose_name="Código",
        related_name='descriptions',
        default=None,
        blank=True,
        )
    description = models.TextField(
        verbose_name="Descrição",
        unique=True,
        )
    source_files = models.ManyToManyField(
        SourceFile,
        verbose_name='Arquivos de origem',
        related_name='descriptions',
        default=None,
        blank=True,
        )
    group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=GENERIC_GROUP,
        default=None,
        )

    class Meta:
        verbose_name="Descrição genérica"
        verbose_name_plural="Descrições genéricas"
        constraints = [
            models.UniqueConstraint(
               fields=['description',],
               name="unique_generic_description"
            )
        ]

    def __str__(self):
        return str(self.description)

 
class MonetaryValue(models.Model):

    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        related_name='values',
        default=None,
        null=True,
        blank=True,
        )
    source_file = models.ForeignKey(
        SourceFile,
        verbose_name="Arquivo de origem",
        on_delete=models.CASCADE,
        related_name='values',
        default=None,
        null=True,
        blank=True,
    )
    monetary_value = models.DecimalField(
        verbose_name="Valor monetário",
        max_digits=12,
        decimal_places=4,
        default=Decimal(0.0),
        )
    unit = models.ForeignKey(
        Unit,
        verbose_name='Unidade',
        on_delete=models.CASCADE,
        related_name='values',
        default=None,
        null=True,
        blank=True,
        )
    classification = models.CharField(
        verbose_name="Classificação",
        max_length=2,
        choices=MONETARY,
        default=CUSTO,
        )
    group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=GENERIC_GROUP,
        default=None,
        )

    class Meta:
        verbose_name="Valor monetário"
        verbose_name_plural="Valores monetários"
        constraints = [
            models.UniqueConstraint(
               fields=['generic_item', 'source_file', 'classification'],
               name="unique_monetary_value"
            )
        ]


class Composition(models.Model):

    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        related_name='compositions',
        default=None,
        null=True,
        blank=True,
        )
    generic_description = models.ForeignKey(
        GenericDescription,
        verbose_name="Descrição",
        on_delete=models.CASCADE,
        related_name='compositions',
        default=None,
        null=True,
        blank=True,
        )
    unit = models.ForeignKey(
        Unit,
        verbose_name='Unidade',
        on_delete=models.CASCADE,
        related_name='compositions',
        default=None,
        null=True,
        blank=True,
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
    source_file = models.ForeignKey(
        SourceFile,
        verbose_name='Arquivo de origem',
        on_delete=models.CASCADE,
        related_name='compositions',
        default=None,
        null=True,
        blank=True,
        )
    composition_group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=COMPOSITION_GROUP,
        )


    class Meta:
        verbose_name="Composição"
        verbose_name_plural="Composições"
        constraints = [
            models.UniqueConstraint(
               fields=['generic_item', 'source_file'],
               name="unique_composition"
            )
        ]

    def __str__(self):
        return str(self.generic_item) + ' - ' + str(self.generic_description)


class InputItem(models.Model):

    composition = models.ForeignKey(
        Composition,
        verbose_name="Composição",
        on_delete=models.CASCADE,
        related_name='inputs',
        default=None,
        null=True,
        blank=True,
        )
    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        related_name='inputs',
        default=None,
        null=True,
        blank=True,
        )
    generic_description = models.ForeignKey(
        GenericDescription,
        verbose_name="Descrição",
        on_delete=models.CASCADE,
        related_name='inputs',
        default=None,
        null=True,
        blank=True,
        )
    input_group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=INPUT_GROUP,
        )
    input_quantity = models.DecimalField(
        verbose_name="Quantidade",
        max_digits=18,
        decimal_places=5,
        )
    input_use = models.DecimalField(
        verbose_name="Utilização",
        max_digits=18,
        decimal_places=5,
        default=1.0,
        null=True,
        blank=True,
        )

    class Meta:
        verbose_name="Insumo"
        verbose_name_plural="Insumos"
        constraints = [
            models.UniqueConstraint(
               fields=['composition', 'generic_item'],
               name="unique_input"
            )
        ]
    
    def __str__(self):
        return str(self.composition) + ' - ' + str(self.generic_item) + ' - ' + str(self.generic_description)


class TransportItem(models.Model):

    composition = models.ForeignKey(
        Composition,
        verbose_name="Composição",
        on_delete=models.CASCADE,
        related_name='transports',
        default=None,
        null=True,
        blank=True,
        )
    related_input = models.ForeignKey(
        Composition,
        verbose_name='Insumo proprietário',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )
    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        related_name='transports',
        default=None,
        null=True,
        blank=True,
        )
    generic_description = models.ForeignKey(
        GenericDescription,
        verbose_name="Descrição",
        on_delete=models.CASCADE,
        related_name='transports',
        default=None,
        null=True,
        blank=True,
        )
    unit = models.ForeignKey(
        Unit,
        verbose_name='Unidade',
        on_delete=models.CASCADE,
        related_name='transports',
        default=None,
        null=True,
        blank=True,
        )
    transport_group = models.CharField(
        verbose_name="Grupo",
        max_length=2,
        choices=INPUT_GROUP,
        )
    
    class Meta:
        verbose_name="Transporte"
        verbose_name_plural="Transportes"
        constraints = [
            models.UniqueConstraint(
               fields=['composition', 'related_input', 'generic_item', 'generic_description', 'unit', 'transport_group'],
               name="unique_transport"
            )
        ]