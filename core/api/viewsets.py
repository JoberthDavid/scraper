
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework.viewsets import ModelViewSet
from core.models import SourceFile, Composition, InputItem, Unit, GenericItem, GenericDescription
from core.api.serializers import SourceFileSerializer, UnitSerializer, GenericItemSerializer, GenericDescriptionSerializer, CompositionSerializer
from core.api.filters import GenericItemFilter, GenericDescriptionFilter, CompositionFilter


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

    def get_queryset(self):           
        return SourceFile.objects.filter(status=True)
    

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