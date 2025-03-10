from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Patient, Doctor, Bookings
from .serializer import PatientSerializer, DoctorSerializer


class SignUpView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        role = request.data.get('role')
        
        if role == 'patient':
            serializer = PatientSerializer(data=request.data)
        elif role == 'doctor':
            serializer = DoctorSerializer(data=request.data)
        else:
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'{role.capitalize()} signed up successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = Patient.objects.get(email=email)
        except Patient.DoesNotExist:
            user = None

        if user is None:
            try:
                user = Doctor.objects.get(email=email)
            except Doctor.DoesNotExist:
                return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful.',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'role': user.role, 
        }, status=status.HTTP_200_OK)
        
        
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated]
    
