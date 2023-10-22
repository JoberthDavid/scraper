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
    

class Composition(models.Model):

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
    source_file = models.ForeignKey(
        SourceFile,
        verbose_name='Arquivo de origem',
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


    class Meta:
        verbose_name="Composição"
        verbose_name_plural="Composições"
        constraints = [
            models.UniqueConstraint(
               fields=['composition_code', 'fic', 'production', 'source_file'],
               name="unique_composition"
            )
        ]

    def __str__(self):
        return str(self.composition_code)


class InputItem(models.Model):

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
        Composition,
        verbose_name='Composição proprietária',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )

    class Meta:
        verbose_name="Apropriação"
        verbose_name_plural="Apropriações"
        constraints = [
            models.UniqueConstraint(
               fields=['main_input_code', 'main_input_quantity', 'main_input_use', 'transported_input_code', 'related_composition'],
               name="unique_input"
            )
        ]

    def __str__(self):
        return str(self.related_composition) + " - " + str(self.main_input_code)


class Unit(models.Model):

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
    unit = models.ForeignKey(
        Unit,
        verbose_name='Unidade',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
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
               fields=['code', 'unit'],
               name="unique_generic_item"
            )
        ]

    def __str__(self):
        return str(self.code)


class GenericDescription(models.Model):

    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        default=None,
        null=True,
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
        return str(self.generic_item) + " - " + str(self.description)


class UnitaryPrice(models.Model):

    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )
    source_file = models.ForeignKey(
        SourceFile,
        verbose_name="Arquivo de origem",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )
    unitary_price = models.DecimalField(
        verbose_name="Preço unitário",
        max_digits=12,
        decimal_places=4,
        default=Decimal(0.0),
        )

    class Meta:
        verbose_name="Preço unitário"
        verbose_name_plural="Preços unitários"
        constraints = [
            models.UniqueConstraint(
               fields=['generic_item', 'source_file'],
               name="unique_unitary_price"
            )
        ]


class UnitaryCost(models.Model):

    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )
    source_file = models.ForeignKey(
        SourceFile,
        verbose_name="Arquivo de origem",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )
    unitary_cost = models.DecimalField(
        verbose_name="Custo unitário",
        max_digits=12,
        decimal_places=4,
        default=Decimal(0.0),
        )

    class Meta:
        verbose_name="Custo unitário"
        verbose_name_plural="Custos unitários"
        constraints = [
            models.UniqueConstraint(
               fields=['generic_item', 'source_file'],
               name="unique_unitary_cost"
            )
        ]


class ProductiveCost(models.Model):

    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )
    source_file = models.ForeignKey(
        SourceFile,
        verbose_name="Arquivo de origem",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )
    productive_cost = models.DecimalField(
        verbose_name="Custo produtivo",
        max_digits=12,
        decimal_places=4,
        default=Decimal(0.0),
        )

    class Meta:
        verbose_name="Custo produtivo"
        verbose_name_plural="Custo produtivo"
        constraints = [
            models.UniqueConstraint(
               fields=['generic_item', 'source_file'],
               name="unique_productive_cost"
            )
        ]


class UnproductiveCost(models.Model):

    generic_item = models.ForeignKey(
        GenericItem,
        verbose_name="Código",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        )
    source_file = models.ForeignKey(
        SourceFile,
        verbose_name="Arquivo de origem",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )
    unproductive_cost = models.DecimalField(
        verbose_name="Custo improdutivo",
        max_digits=12,
        decimal_places=4,
        default=Decimal(0.0),
        )

    class Meta:
        verbose_name="Custo improdutivo"
        verbose_name_plural="Custo improdutivo"
        constraints = [
            models.UniqueConstraint(
               fields=['generic_item', 'source_file'],
               name="unique_unproductive_cost"
            )
        ]