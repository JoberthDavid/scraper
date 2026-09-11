import django_filters

from core.models import (
SourceFile,
GenericItem,
GenericDescription,
MonetaryValue,
Composition,
)

class SourceFileFilter(django_filters.FilterSet):
    """
    Filtros para arquivos-base.

    ```
    Os filtros existentes são preservados para manter
    compatibilidade com a API atual.

    Novas formas explícitas de consulta são disponibilizadas
    através dos sufixos:

        __exact
        __in
        __startswith
    """

    data_base = django_filters.DateFilter(
        field_name="data_base",
        lookup_expr="exact",
    )

    data_base__gte = django_filters.DateFilter(
        field_name="data_base",
        lookup_expr="gte",
    )

    data_base__lte = django_filters.DateFilter(
        field_name="data_base",
        lookup_expr="lte",
    )

    data_base__year__gte = django_filters.NumberFilter(
        field_name="data_base",
        lookup_expr="year__gte",
    )

    data_base__year__lte = django_filters.NumberFilter(
        field_name="data_base",
        lookup_expr="year__lte",
    )

    methodology = django_filters.CharFilter(
        field_name="methodology",
        lookup_expr="startswith",
    )

    methodology__exact = django_filters.CharFilter(
        field_name="methodology",
        lookup_expr="exact",
    )

    methodology__in = django_filters.BaseInFilter(
        field_name="methodology",
        lookup_expr="in",
    )

    methodology__startswith = django_filters.CharFilter(
        field_name="methodology",
        lookup_expr="startswith",
    )

    uf = django_filters.CharFilter(
        field_name="uf",
        lookup_expr="startswith",
    )

    uf__exact = django_filters.CharFilter(
        field_name="uf",
        lookup_expr="exact",
    )

    uf__in = django_filters.BaseInFilter(
        field_name="uf",
        lookup_expr="in",
    )

    uf__startswith = django_filters.CharFilter(
        field_name="uf",
        lookup_expr="startswith",
    )

    type_system = django_filters.CharFilter(
        field_name="type_system",
        lookup_expr="startswith",
    )

    type_system__exact = django_filters.CharFilter(
        field_name="type_system",
        lookup_expr="exact",
    )

    type_system__in = django_filters.BaseInFilter(
        field_name="type_system",
        lookup_expr="in",
    )

    type_system__startswith = django_filters.CharFilter(
        field_name="type_system",
        lookup_expr="startswith",
    )

    type_file = django_filters.CharFilter(
        field_name="type_file",
        lookup_expr="startswith",
    )

    type_file__exact = django_filters.CharFilter(
        field_name="type_file",
        lookup_expr="exact",
    )

    type_file__in = django_filters.BaseInFilter(
        field_name="type_file",
        lookup_expr="in",
    )

    type_file__startswith = django_filters.CharFilter(
        field_name="type_file",
        lookup_expr="startswith",
    )

    status = django_filters.BooleanFilter(
        field_name="status",
        lookup_expr="exact",
    )

    class Meta:
        model = SourceFile
        fields = [
            "data_base",
            "data_base__gte",
            "data_base__lte",
            "data_base__year__gte",
            "data_base__year__lte",
            "methodology",
            "methodology__exact",
            "methodology__in",
            "methodology__startswith",
            "uf",
            "uf__exact",
            "uf__in",
            "uf__startswith",
            "type_system",
            "type_system__exact",
            "type_system__in",
            "type_system__startswith",
            "type_file",
            "type_file__exact",
            "type_file__in",
            "type_file__startswith",
            "status",
        ]


class GenericItemFilter(django_filters.FilterSet):
    """
    Filtros para itens genéricos.

    ```
    Compatibilidade atual:

        code=E
        code=P98
        code=M00

    continua significando busca por prefixo.

    Novos filtros:

        code__exact
        code__in
        code__startswith
    """

    source_files = django_filters.DateFilter(
        field_name="source_files__data_base",
        lookup_expr="exact",
    )

    source_files__in = django_filters.BaseInFilter(
        field_name="source_files__data_base",
        lookup_expr="in",
    )

    code = django_filters.CharFilter(
        field_name="code",
        lookup_expr="startswith",
    )

    code__exact = django_filters.CharFilter(
        field_name="code",
        lookup_expr="exact",
    )

    code__in = django_filters.BaseInFilter(
        field_name="code",
        lookup_expr="in",
    )

    code__startswith = django_filters.CharFilter(
        field_name="code",
        lookup_expr="startswith",
    )

    descriptions = django_filters.CharFilter(
        field_name="descriptions__description",
        lookup_expr="startswith",
    )

    descriptions__exact = django_filters.CharFilter(
        field_name="descriptions__description",
        lookup_expr="exact",
    )

    descriptions__startswith = django_filters.CharFilter(
        field_name="descriptions__description",
        lookup_expr="startswith",
    )

    descriptions__group = django_filters.CharFilter(
        field_name="descriptions__group",
        lookup_expr="startswith",
    )

    descriptions__group__exact = django_filters.CharFilter(
        field_name="descriptions__group",
        lookup_expr="exact",
    )

    descriptions__group__in = django_filters.BaseInFilter(
        field_name="descriptions__group",
        lookup_expr="in",
    )

    descriptions__group__startswith = django_filters.CharFilter(
        field_name="descriptions__group",
        lookup_expr="startswith",
    )

    class Meta:
        model = GenericItem
        fields = [
            "source_files",
            "source_files__in",
            "code",
            "code__exact",
            "code__in",
            "code__startswith",
            "descriptions",
            "descriptions__exact",
            "descriptions__startswith",
            "descriptions__group",
            "descriptions__group__exact",
            "descriptions__group__in",
            "descriptions__group__startswith",
        ]


class GenericDescriptionFilter(django_filters.FilterSet):
    """
    Filtros para descrições genéricas.

    ```
    Os filtros existentes por prefixo são preservados.
    """

    source_files = django_filters.DateFilter(
        field_name="source_files__data_base",
        lookup_expr="exact",
    )

    source_files__in = django_filters.BaseInFilter(
        field_name="source_files__data_base",
        lookup_expr="in",
    )

    group = django_filters.CharFilter(
        field_name="group",
        lookup_expr="startswith",
    )

    group__exact = django_filters.CharFilter(
        field_name="group",
        lookup_expr="exact",
    )

    group__in = django_filters.BaseInFilter(
        field_name="group",
        lookup_expr="in",
    )

    group__startswith = django_filters.CharFilter(
        field_name="group",
        lookup_expr="startswith",
    )

    generic_item = django_filters.CharFilter(
        field_name="generic_items__code",
        lookup_expr="startswith",
    )

    generic_item__exact = django_filters.CharFilter(
        field_name="generic_items__code",
        lookup_expr="exact",
    )

    generic_item__in = django_filters.BaseInFilter(
        field_name="generic_items__code",
        lookup_expr="in",
    )

    generic_item__startswith = django_filters.CharFilter(
        field_name="generic_items__code",
        lookup_expr="startswith",
    )

    description = django_filters.CharFilter(
        field_name="description",
        lookup_expr="startswith",
    )

    description__exact = django_filters.CharFilter(
        field_name="description",
        lookup_expr="exact",
    )

    description__startswith = django_filters.CharFilter(
        field_name="description",
        lookup_expr="startswith",
    )

    class Meta:
        model = GenericDescription
        fields = [
            "source_files",
            "source_files__in",
            "group",
            "group__exact",
            "group__in",
            "group__startswith",
            "generic_item",
            "generic_item__exact",
            "generic_item__in",
            "generic_item__startswith",
            "description",
            "description__exact",
            "description__startswith",
        ]


class MonetaryValueFilter(django_filters.FilterSet):
    """
    Filtros para valores monetários.

    ```
    Compatibilidade atual:

        generic_item=E
        generic_item=P98
        generic_item=M00

    continua significando busca por prefixo.

    Novos filtros:

        generic_item__exact
        generic_item__in
        generic_item__startswith

    O filtro `generic_item__in` é o principal recurso
    necessário para o motor de cálculo.
    """

    source_file = django_filters.DateFilter(
        field_name="source_file__data_base",
        lookup_expr="exact",
    )

    source_file__in = django_filters.BaseInFilter(
        field_name="source_file__data_base",
        lookup_expr="in",
    )

    type_system = django_filters.CharFilter(
        field_name="type_system",
        lookup_expr="startswith",
    )

    type_system__exact = django_filters.CharFilter(
        field_name="type_system",
        lookup_expr="exact",
    )

    type_system__in = django_filters.BaseInFilter(
        field_name="type_system",
        lookup_expr="in",
    )

    type_system__startswith = django_filters.CharFilter(
        field_name="type_system",
        lookup_expr="startswith",
    )

    classification = django_filters.CharFilter(
        field_name="classification",
        lookup_expr="startswith",
    )

    classification__exact = django_filters.CharFilter(
        field_name="classification",
        lookup_expr="exact",
    )

    classification__in = django_filters.BaseInFilter(
        field_name="classification",
        lookup_expr="in",
    )

    classification__startswith = django_filters.CharFilter(
        field_name="classification",
        lookup_expr="startswith",
    )

    group = django_filters.CharFilter(
        field_name="group",
        lookup_expr="startswith",
    )

    group__exact = django_filters.CharFilter(
        field_name="group",
        lookup_expr="exact",
    )

    group__in = django_filters.BaseInFilter(
        field_name="group",
        lookup_expr="in",
    )

    group__startswith = django_filters.CharFilter(
        field_name="group",
        lookup_expr="startswith",
    )

    generic_item = django_filters.CharFilter(
        field_name="generic_item__code",
        lookup_expr="startswith",
    )

    generic_item__exact = django_filters.CharFilter(
        field_name="generic_item__code",
        lookup_expr="exact",
    )

    generic_item__in = django_filters.BaseInFilter(
        field_name="generic_item__code",
        lookup_expr="in",
    )

    generic_item__startswith = django_filters.CharFilter(
        field_name="generic_item__code",
        lookup_expr="startswith",
    )

    unit = django_filters.CharFilter(
        field_name="unit__unit",
        lookup_expr="startswith",
    )

    unit__exact = django_filters.CharFilter(
        field_name="unit__unit",
        lookup_expr="exact",
    )

    unit__in = django_filters.BaseInFilter(
        field_name="unit__unit",
        lookup_expr="in",
    )

    unit__startswith = django_filters.CharFilter(
        field_name="unit__unit",
        lookup_expr="startswith",
    )

    class Meta:
        model = MonetaryValue
        fields = [
            "source_file",
            "source_file__in",
            "type_system",
            "type_system__exact",
            "type_system__in",
            "type_system__startswith",
            "classification",
            "classification__exact",
            "classification__in",
            "classification__startswith",
            "group",
            "group__exact",
            "group__in",
            "group__startswith",
            "generic_item",
            "generic_item__exact",
            "generic_item__in",
            "generic_item__startswith",
            "unit",
            "unit__exact",
            "unit__in",
            "unit__startswith",
        ]


class CompositionFilter(django_filters.FilterSet):
    """
    Filtros para composições.

    ```
    Os comportamentos existentes são preservados e
    são acrescentadas formas explícitas de consulta.
    """

    source_files__data_base = django_filters.DateFilter(
        field_name="source_files__data_base",
        lookup_expr="exact",
    )

    source_files__data_base__in = django_filters.BaseInFilter(
        field_name="source_files__data_base",
        lookup_expr="in",
    )

    composition_group = django_filters.CharFilter(
        field_name="composition_group",
        lookup_expr="startswith",
    )

    composition_group__exact = django_filters.CharFilter(
        field_name="composition_group",
        lookup_expr="exact",
    )

    composition_group__in = django_filters.BaseInFilter(
        field_name="composition_group",
        lookup_expr="in",
    )

    composition_group__startswith = django_filters.CharFilter(
        field_name="composition_group",
        lookup_expr="startswith",
    )

    generic_item__code = django_filters.CharFilter(
        field_name="generic_item__code",
        lookup_expr="exact",
    )

    generic_item__code__in = django_filters.BaseInFilter(
        field_name="generic_item__code",
        lookup_expr="in",
    )

    generic_item__code__startswith = django_filters.CharFilter(
        field_name="generic_item__code",
        lookup_expr="startswith",
    )

    generic_item = django_filters.CharFilter(
        field_name="generic_item__code",
        lookup_expr="exact",
    )

    generic_item__in = django_filters.BaseInFilter(
        field_name="generic_item__code",
        lookup_expr="in",
    )

    generic_item__startswith = django_filters.CharFilter(
        field_name="generic_item__code",
        lookup_expr="startswith",
    )

    generic_description__description = django_filters.CharFilter(
        field_name="generic_description__description",
        lookup_expr="startswith",
    )

    generic_description__description__exact = django_filters.CharFilter(
        field_name="generic_description__description",
        lookup_expr="exact",
    )

    generic_description__description__startswith = django_filters.CharFilter(
        field_name="generic_description__description",
        lookup_expr="startswith",
    )

    class Meta:
        model = Composition
        fields = [
            "source_files__data_base",
            "source_files__data_base__in",
            "composition_group",
            "composition_group__exact",
            "composition_group__in",
            "composition_group__startswith",
            "generic_item__code",
            "generic_item__code__in",
            "generic_item__code__startswith",
            "generic_item",
            "generic_item__in",
            "generic_item__startswith",
            "generic_description__description",
            "generic_description__description__exact",
            "generic_description__description__startswith",
        ]