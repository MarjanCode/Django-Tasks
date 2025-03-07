from rest_framework import serializers

class UnitConversionSerializer(serializers.Serializer):
    value = serializers.FloatField()
    from_unit = serializers.CharField()
    to_unit = serializers.CharField()