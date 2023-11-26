from rest_framework import serializers
from core.models import SourceFile, GenericItem, GenericDescription, Unit, MonetaryValue, Composition, InputItem


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

    class Meta:
        model = GenericItem
        fields = ['id', 'code', 'source_files', 'group']


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ['id', 'unit']


class MonetaryValueSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')

    class Meta:
        model = MonetaryValue
        fields = ['id', 'generic_item', 'monetary_value', 'unit', 'classification', 'group']

class InputItemSerializer(serializers.ModelSerializer):

    composition = serializers.PrimaryKeyRelatedField(read_only=True)
    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InputItem
        fields = ['id', 'composition', 'generic_item', 'generic_description', 'input_group', 'input_quantity', 'input_use']

class CompositionSerializer(serializers.ModelSerializer):

    generic_item = serializers.SlugRelatedField(read_only=True, slug_field='code')
    generic_description = serializers.StringRelatedField(read_only=True)
    unit = serializers.SlugRelatedField(read_only=True, slug_field='unit')
    source_file = serializers.SlugRelatedField(read_only=True, slug_field='data_base')
    inputs = InputItemSerializer(many=True, read_only=True)

    class Meta:
        model = Composition
        fields = ['id', 'composition_group', 'generic_item', 'generic_description', 'unit', 'fic', 'production','source_file', 'inputs']
 