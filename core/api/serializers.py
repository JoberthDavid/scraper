from rest_framework import serializers
from core.models import SourceFile, Composition, EquipmentItem, WorkmanItem, MaterialItem, AuxiliaryActivityItem, TransportItem, GenericItem, GenericDescription, Unit, MonetaryValue


class SourceFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = SourceFile
        fields = ['id', 'methodology',  'uf', 'data_base', 'source_file','type_system', 'type_file', 'status']


class GenericDescriptionSerializer(serializers.ModelSerializer):

    source_files = serializers.SlugRelatedField(many=True, read_only=True, slug_field='data_base')
    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')

    class Meta:
        model = GenericDescription
        fields = ['id', 'source_files', 'generic_item', 'group', 'description']       


class GenericItemSerializer(serializers.ModelSerializer):

    source_files = serializers.SlugRelatedField(many=True, read_only=True, slug_field='data_base')
    descriptions = GenericDescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = GenericItem
        fields = ['id', 'code', 'source_files', 'descriptions']


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ['id', 'unit']


class MonetaryValueSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')

    class Meta:
        model = MonetaryValue
        fields = ['source_file', 'type_system', 'id', 'generic_item', 'monetary_value', 'unit', 'classification', 'group']


class EquipmentItemSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')

    class Meta:
        model = EquipmentItem
        fields = ['id', 'input_group', 'generic_item', 'generic_description', 'unit', 'input_quantity', 'input_use']


class WorkmanItemSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')

    class Meta:
        model = WorkmanItem
        fields = ['id', 'input_group', 'generic_item', 'generic_description', 'unit', 'input_quantity']


class MaterialItemSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')

    class Meta:
        model = MaterialItem
        fields = ['id', 'input_group', 'generic_item', 'generic_description', 'unit', 'input_quantity']


class AuxiliaryActivityItemSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')

    class Meta:
        model = AuxiliaryActivityItem
        fields = ['id', 'input_group', 'generic_item', 'generic_description', 'unit', 'input_quantity']


class TransportItemSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')
    proprietary_item = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TransportItem
        fields = ['id', 'input_group', 'generic_item', 'generic_description', 'unit', 'input_quantity', 'proprietary_item']


class CompositionSerializer(serializers.ModelSerializer):

    source_files = SourceFileSerializer(many=True, read_only=True)
    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')
    equipments = EquipmentItemSerializer(many=True, read_only=True)
    workmen = WorkmanItemSerializer(many=True, read_only=True)
    materials = MaterialItemSerializer(many=True, read_only=True)
    activities = AuxiliaryActivityItemSerializer(many=True, read_only=True)
    transports = TransportItemSerializer(many=True, read_only=True)

    class Meta:
        model = Composition
        fields = ['source_files', 'id', 'composition_group', 'generic_item', 'generic_description', 'unit', 'fic', 'production', 'equipments', 'workmen', 'materials', 'activities', 'transports']