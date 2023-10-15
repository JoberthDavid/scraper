from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework.viewsets import ModelViewSet
from core.models import SourceFile, Composition, InputItem, Unit, GenericItem, GenericDescription
from core.api.serializers import SourceFileSerializer, UnitSerializer, GenericItemSerializer


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
    

class SourceFileViewSet(ModelViewSet):

    serializer_class = SourceFileSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        methodology = self.request.query_params.get('methodology')
        type_system = self.request.query_params.get('type_system')
        data_base = self.request.query_params.get('data_base')

        queryset = SourceFile.objects.filter(status=True)

        if methodology:
            queryset = SourceFile.objects.filter(methodology=methodology)
        if type_system:
            queryset = SourceFile.objects.filter(type_system=type_system)
        if data_base:
            queryset = SourceFile.objects.filter(data_base=data_base)
            
        return queryset
    

class GenericItemViewSet(ModelViewSet):

    serializer_class = GenericItemSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        code = self.request.query_params.get('code')
        unit = self.request.query_params.get('unit')
        source_files = self.request.query_params.get('source_files')
        group = self.request.query_params.get('group')

        queryset = GenericItem.objects.all()

        if code:
            queryset = GenericItem.objects.filter(code=code)
        if unit:
            queryset = GenericItem.objects.filter(unit=unit)
        if source_files:
            queryset = GenericItem.objects.filter(source_files=source_files)
        if group:
            queryset = GenericItem.objects.filter(group=group)
            
        return queryset