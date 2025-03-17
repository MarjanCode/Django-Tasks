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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload, None 
    except jwt.ExpiredSignatureError:
        return None, "Token has expired."
    except jwt.InvalidTokenError:
        return None, "Invalid token."

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
    
    def put(self, request):
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
    
    def delete(self, request, doctor_id=None):
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

        # Delete whole doctor profile (DELETE /api/v1/doctors/)
        if doctor_id is None:
            doctor.delete()
            return Response({
                'success': True,
                'message': 'Doctor profile deleted successfully.'
            }, status=status.HTTP_200_OK)

        # Delete a slot (DELETE /api/v1/doctors/<int:doctor_id>/)
        slot_data = request.data.get("available_slots", [])
        if not slot_data:
            return Response({
                'success': False,
                'message': '"available_slots" is required in request body.'
            }, status=status.HTTP_400_BAD_REQUEST)

        date_to_delete = slot_data[0].get("date")
        slots_to_delete = slot_data[0].get("slots")

        if not date_to_delete or not slots_to_delete:
            return Response({
                'success': False,
                'message': 'Both "date" and "slots" are required in "available_slots".'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update available_slots safely
        new_slots = []
        slot_found = False

        for slot in doctor.available_slots:
            if slot["date"] == date_to_delete:
                slot["slots"] = [s for s in slot["slots"] if s not in slots_to_delete]
                slot_found = True

            if slot["slots"]:  # Keep only slots that still have times
                new_slots.append(slot)

        if not slot_found:
            return Response({
                'success': False,
                'message': 'The specified slot(s) and date were not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        doctor.available_slots = new_slots
        doctor.save()

        return Response({
            'success': True,
            'message': 'The specified slot(s) were deleted successfully.'
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
           
        if Booking.objects.filter(doctor_id=doctor_id, date=date, time_slot=time_slot).exists():
             return Response({
                 "success": False,
                 "message": "The requested time slot is not available."
             }, status=status.HTTP_400_BAD_REQUEST)
        
        booking = serializer.save(user=user, status='confirmed', doctor=doctor) # added
        return Response({
            "success": True,
            "message": "Booking confirmed!",
            "booking": BookingSerializer(booking).data
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request, booking_id):
        user, error_message = get_user_from_token(request)
        if not user:
            return Response({
                "success": False,
                'message': error_message
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            booking  = Booking.objects.get(id=booking_id)
            is_patient = booking.user == user
            is_doctor = Doctor.objects.filter(user=user, id=booking.doctor.id).exists()

            if not (is_patient or is_doctor):
                return Response({
                    'success': False, 
                    'message': 'You do not have permission to delete this appointment.'
                }, status=status.HTTP_403_FORBIDDEN)
        
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
