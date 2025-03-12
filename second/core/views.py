from datetime import datetime, timedelta, timezone
import jwt
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from .serializer import UserSerializer, DoctorSerializer, BookingsSerializer
from .models import User, Doctor, Bookings
from django.conf import settings
import requests


def generate_jwt_token(user):
    payload = {
        'email': user.email,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None


@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()  
        return Response({'message': 'User signed up successfully.'}, status=status.HTTP_201_CREATED)

    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, user.password):
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token = generate_jwt_token(user)
    return Response({
        'message': 'Login successful.',
        'access_token': token,
    }, status=status.HTTP_200_OK)


class DoctorProfileAPIView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'message': 'Authorization header missing or invalid.'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)

        if not payload:
            return Response({'message': 'Invalid or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)

        email = payload.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({
            'success': False,
            'message': 'User with this email does not exist.'
        }, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = DoctorSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid data.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=user)
        return Response({
            'success': True,
            'message': 'Doctor profile created successfully.',
            'doctor_id': serializer.data['id']
        }, status=status.HTTP_201_CREATED)
        

class BookAppointmentAPIView(APIView):
    def post(self, request):
        serializer = BookingsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid request data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        doctor_id = serializer.validated_data['doctor_id']
        date = serializer.validated_data['date']
        time_slot = serializer.validated_data['time_slot']

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({
                "success": False,
                "message": "Doctor not found."
            }, status=status.HTTP_404_NOT_FOUND)

        if Bookings.objects.filter(doctor_id=doctor_id, date=date, time_slot=time_slot).exists():
            return Response({
                "success": False,
                "message": "The requested time slot is not available."
            }, status=status.HTTP_400_BAD_REQUEST)

        booking = serializer.save(status='confirmed')

        # send sms 
        self.send_sms_notification(booking, doctor)

        return Response({
            "success": True,
            "message": "Booking confirmed!",
            "booking": BookingsSerializer(booking).data
        }, status=status.HTTP_201_CREATED)
    # sms function
    def send_sms_notification(self, booking, doctor):
        message = f"Dear User, your appointment with Dr. {doctor.name} is confirmed for {booking.date} at {booking.time_slot}. Thank you!"

        try:
            requests.post(
                'https://api.sms.ir/v1/send',
                json={'mobile': booking.phone_number, 'message': message},
                headers={'X-API-KEY': 'your_sms_ir_api_key', 'Content-Type': 'application/json'}
        ).raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send SMS: {e}")
