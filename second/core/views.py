from datetime import datetime, timedelta, timezone
import jwt
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from .serializer import UserSerializer, DoctorSerializer, BookingSerializer
from .models import User, Doctor, Booking
from django.conf import settings


def generate_jwt_token(user):
    payload = {
        'email': user.email,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    # this version is better to debug! : 
    # token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    # return token


def decode_jwt_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired.'
    except jwt.InvalidTokenError:
        return None, 'Invalid token.'


def get_user_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, 'Authorization header missing or invalid.'

    # decode the token
    token = auth_header.split(' ')[1]
    payload, error_message = decode_jwt_token(token)
    if not payload:
        return None, error_message

    # Fetch the user
    email = payload.get('email')
    user = User.objects.filter(email=email).first()
    if not user:
        return None, 'User with this email does not exist.'

    return user, None


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

    user = User.objects.filter(email=email).first()
    if not user or not check_password(password, user.password):
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token = generate_jwt_token(user)
    return Response({
        'message': 'Login successful.',
        'access_token': token,
    }, status=status.HTTP_200_OK)


class DoctorProfileAPIView(APIView): 
    def post(self, request):
        user, error_message = get_user_from_token(request)
        if not user:
            return Response({
                'success': False,
                'message': error_message
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = DoctorSerializer(data=request.data)
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
    
    def patch(self, request):
        user, error_message = get_user_from_token(request)
        if not user:
            return Response({
                'success': False,
                'message': error_message
            }, status=status.HTTP_401_UNAUTHORIZED) 
            
        try:
            doctor = Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Doctor profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)          

        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid data.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({
            'success': True,
            'message': 'Doctor profile updated successfully.',
            'doctor': serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request):
        user, error_message = get_user_from_token(request)
        if not user:
            return Response({
                'success': False,
                'message': error_message
            }, status=status.HTTP_401_UNAUTHORIZED)
                            
        try:
            doctor = Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Doctor profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
            
        doctor.delete()
        
        return Response({
            'success': True,
            'message': 'Doctor profile deleted successfully.'
        }, status=status.HTTP_200_OK)
        
    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response({
            'success': True,
            'doctors': serializer.data
        }, status=status.HTTP_200_OK)
        

class BookAppointmentAPIView(APIView):
    def post(self, request):
        user, error_message = get_user_from_token(request)
        if not user:
            return Response({
                "success": False,
                'message': error_message
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = BookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid request data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        doctor_id = serializer.validated_data['doctor_id']
        date = serializer.validated_data['date']
        time_slot = serializer.validated_data['time_slot']
        
        # if not Doctor.objects.filter(id=doctor_id).exists():
        #     return Response({
        #         "success": False,
        #         "message": "Doctor not found."
        #     }, status=status.HTTP_404_NOT_FOUND)
            
        # If you need the doctor object for further processing:
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({
                "success": False,
                "message": "Doctor not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
            
        slot_to_book = {"date": str(date), "time_slot": time_slot}
        if slot_to_book not in doctor.available_slots:
            return Response({
                "success": False,
                "message": "The requested time slot is not available."
            }, status=status.HTTP_400_BAD_REQUEST)
    
        doctor.available_slots = [slot for slot in doctor.available_slots if slot != slot_to_book]
        doctor.save()

        # if Booking.objects.filter(doctor_id=doctor_id, date=date, time_slot=time_slot).exists():
        #     return Response({
        #         "success": False,
        #         "message": "The requested time slot is not available."
        #     }, status=status.HTTP_400_BAD_REQUEST)

        booking = serializer.save(user=user, status='confirmed', doctor=doctor) # added
        return Response({
            "success": True,
            "message": "Booking confirmed!",
            "booking": BookingSerializer(booking).data
        }, status=status.HTTP_201_CREATED)
    
    def patch(self, request, booking_id):
        user, error_message = get_user_from_token(request)
        if not user:
            return Response({
                "success": False,
                'message': error_message
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            booking = Booking.objects.get(id=booking_id, user=user)
        except Booking.DoesNotExist:
            return Response({
                "success": False,
                "message": "Booking not found or you do not have permission to update it."
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid request data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if 'doctor_id' in request.data:
            doctor_id = request.data['doctor_id']
            if not Doctor.objects.filter(id=doctor_id).exists():
                return Response({
                    "success": False,
                    "message": "Doctor not found."
                }, status=status.HTTP_404_NOT_FOUND)
                
        if 'date' in request.data or 'time_slot' in request.data:
            new_date = request.data.get('date', booking.date)
            new_time_slot = request.data.get('time_slot', booking.time_slot)
            new_doctor_id = request.data.get('doctor_id', booking.doctor_id)

            if Booking.objects.filter(doctor_id=new_doctor_id, date=new_date, time_slot=new_time_slot).exclude(id=booking_id).exists():
                return Response({
                    "success": False,
                    "message": "The requested time slot is not available."
                }, status=status.HTTP_400_BAD_REQUEST)
                
        serializer.save()
        return Response({
            "success": True,
            "message": "Booking updated successfully.",
            "booking": serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, booking_id):
        user, error_message = get_user_from_token(request)
        if not user:
            return Response({
                "success": False,
                'message': error_message
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            booking  = Booking.objects.get(id=booking_id)
            is_patient = booking .patient == user
            is_doctor = Doctor.objects.filter(user=user, id=booking.doctor.id).exists()

            if not (is_patient or is_doctor):
                return Response({
                    'success': False, 
                    'message': 'You do not have permission to delete this appointment.'
                }, status=status.HTTP_403_FORBIDDEN)

            slot_to_release = {"date": str(booking.date), "time_slot": booking.time_slot}
            booking.doctor.available_slots.append(slot_to_release)
            booking.doctor.save()
        
            booking .delete()
            return Response({
                'success': True,
                'message': 'Appointment deleted successfully.'
            }, status=status.HTTP_200_OK)
         
        except Booking.DoesNotExist:
            return Response({
                'success': False, 
                'message': 'Appointment not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response({
            "success": True,
            "bookings": serializer.data
        }, status=status.HTTP_200_OK)
