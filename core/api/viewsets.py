
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework.viewsets import ModelViewSet
from core.models import SourceFile, Composition, InputItem, Unit, GenericItem, GenericDescription
from core.api.serializers import SourceFileSerializer, UnitSerializer, GenericItemSerializer
from core.api.filters import GenericItemFilter


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
       

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