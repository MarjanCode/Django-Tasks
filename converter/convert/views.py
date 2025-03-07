from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UnitConversionSerializer 

class UnitConversionAPIView(APIView):
    CONVERSION_FACTORS = {
        'ton': {'kg': 1000, 'g': 1_000_000},
        'kg': {'ton': 0.001, 'g': 1000},
        'g': {'ton': 0.000001, 'kg': 0.001},
    }

    def get(self, request):
        serializer = UnitConversionSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        value = serializer.validated_data['value']
        from_unit = serializer.validated_data['from_unit']
        to_unit = serializer.validated_data['to_unit']

        try:
            if from_unit not in self.CONVERSION_FACTORS or to_unit not in self.CONVERSION_FACTORS[from_unit]:
                raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")
            
            result = value * self.CONVERSION_FACTORS[from_unit][to_unit]
            return Response({
                'value': value,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'result': result,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)