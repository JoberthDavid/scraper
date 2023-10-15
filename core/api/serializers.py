from rest_framework.serializers import ModelSerializer
from core.models import SourceFile, Composition, InputItem, Unit, GenericItem, GenericDescription


class GenericItemSerializer(ModelSerializer):

    class Meta:
        model = GenericItem
        fields = ['code', 'unit', 'source_files', 'group']

        
class SourceFileSerializer(ModelSerializer):

    items = GenericItemSerializer(many=True, read_only=True)

    class Meta:
        model = SourceFile
        fields = ['id', 'methodology', 'data_base', 'items', 'uf', 'type_system', 'type_file', 'status']


class UnitSerializer(ModelSerializer):

    class Meta:
        model = Unit
        fields = ['id', 'unit']