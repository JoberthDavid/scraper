
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework.viewsets import ModelViewSet
from core.models import  SourceFile, GenericItem, GenericDescription, Unit, MonetaryValue, Composition, InputItem
from core.api.serializers import SourceFileSerializer, GenericItemSerializer, GenericDescriptionSerializer, UnitSerializer, MonetaryValueSerializer, CompositionSerializer, InputItemSerializer
from core.api.filters import SourceFileFilter, GenericItemFilter, GenericDescriptionFilter, MonetaryValueFilter, CompositionFilter


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
       

class SourceFileViewSet(ModelViewSet):

    serializer_class = SourceFileSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get', ]
    filter_backends = [
            filters.OrderingFilter,
            DjangoFilterBackend,
        ]
    ordering_fields = ['data_base', 'type_system']
    ordering = ['data_base', 'type_system']
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
    ordering_fields = ['description']
    ordering = ['description']
    filterset_class = GenericDescriptionFilter

    def get_queryset(self):           
        return GenericDescription.objects.all()


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
        return GenericItem.objects.all()


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
        return Composition.objects.all()