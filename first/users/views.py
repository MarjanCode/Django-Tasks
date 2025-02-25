from .models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializer import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
def sign_up(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        email = request.data.get('email')
        password = request.data.get('password')
              
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save(email=email, password=password)
        
        return Response({'message': 'User signed up successfully.'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def log_in(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.password != password:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token = RefreshToken.for_user(user)

    return Response({
        'message': 'Login successful.',
        'token': str(token), 
    }, status=status.HTTP_200_OK)
    