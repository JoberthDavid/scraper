
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework.viewsets import ModelViewSet
from core.models import SourceFile, Composition, EquipmentItem, WorkmanItem, MaterialItem, AuxiliaryActivityItem, TransportItem, GenericItem, GenericDescription, Unit, MonetaryValue
from core.api.serializers import SourceFileFullyDetailedSerializer, GenericItemSerializer, GenericDescriptionSerializer, UnitSerializer, MonetaryValueSerializer, CompositionSerializer, EquipmentItemSerializer, WorkmanItemSerializer, MaterialItemSerializer, AuxiliaryActivityItemSerializer, TransportItemSerializer
from core.api.filters import SourceFileFilter, GenericItemFilter, GenericDescriptionFilter, MonetaryValueFilter, CompositionFilter
from core.usefuls.choices import *


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
       

class SourceFileViewSet(ModelViewSet):

    serializer_class = SourceFileFullyDetailedSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['data_base', 'type_system']
    ordering = ['data_base', 'type_file']
    filterset_class = SourceFileFilter         
        
    def get_queryset(self):
        return SourceFile.objects.filter(status=True)


class GenericDescriptionViewSet(ModelViewSet):

    serializer_class = GenericDescriptionSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['group', 'code', 'description']
    ordering = ['group', 'code', 'description']
    filterset_class = GenericDescriptionFilter

    def get_queryset(self):           
        return GenericDescription.objects.prefetch_related('source_files').all()


class GenericItemViewSet(ModelViewSet):

    serializer_class = GenericItemSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['code']
    ordering = ['code']
    filterset_class = GenericItemFilter

    def get_queryset(self):           
        return GenericItem.objects.prefetch_related('source_files').prefetch_related('descriptions').all()


class CompositionItemViewSet(ModelViewSet):

    serializer_class = GenericItemSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['descriptions__group', 'code']
    ordering = ['descriptions__group', 'code']
    filterset_class = GenericItemFilter

    def get_queryset(self):           
        return GenericItem.objects.prefetch_related('source_files').prefetch_related('descriptions').filter(descriptions__group=COMPOSICAO)


class EquipmentItemViewSet(ModelViewSet):

    serializer_class = GenericItemSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['descriptions__group', 'code']
    ordering = ['descriptions__group', 'code']
    filterset_class = GenericItemFilter

    def get_queryset(self):           
        return GenericItem.objects.prefetch_related('source_files').prefetch_related('descriptions').filter(descriptions__group=EQUIPAMENTO)


class WorkmanItemViewSet(ModelViewSet):

    serializer_class = GenericItemSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['descriptions__group', 'code']
    ordering = ['descriptions__group', 'code']
    filterset_class = GenericItemFilter

    def get_queryset(self):           
        return GenericItem.objects.prefetch_related('source_files').prefetch_related('descriptions').filter(descriptions__group=MAODEOBRA)


class MaterialItemViewSet(ModelViewSet):

    serializer_class = GenericItemSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['descriptions__group', 'code']
    ordering = ['descriptions__group', 'code']
    filterset_class = GenericItemFilter

    def get_queryset(self):           
        return GenericItem.objects.prefetch_related('source_files').prefetch_related('descriptions').filter(descriptions__group=MATERIAL)
    

class UnitViewSet(ModelViewSet):

    serializer_class = UnitSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['unit']
    ordering = ['unit']

    def get_queryset(self):           
        return Unit.objects.all()


class MonetaryValueViewSet(ModelViewSet):

    serializer_class = MonetaryValueSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['generic_item', 'unit']
    ordering = ['generic_item', 'unit']
    filterset_class = MonetaryValueFilter
    
    def get_queryset(self):
        data_base = self.request.GET.get('source_files__data_base')

        if data_base:
            return MonetaryValue.objects.filter(
                source_file__data_base=data_base
            )

        return MonetaryValue.objects.all()

class CompositionViewSet(ModelViewSet):

    serializer_class = CompositionSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['composition_group',]
    ordering = ['composition_group',]
    filterset_class = CompositionFilter

    def get_queryset(self):
        data_base = self.request.GET.get('source_files__data_base')
        if data_base:
            return Composition.objects.filter(source_files__data_base=data_base).prefetch_related('source_files')
        else:
            return Composition.objects.prefetch_related('source_files')