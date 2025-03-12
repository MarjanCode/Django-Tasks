from rest_framework import serializers
from .models import User, Doctor, Bookings
from django.contrib.auth.hashers import make_password



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password']
        
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
        

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'name', 'specialty', 'available_slots']

    def validate_user(self, value):
        if Doctor.objects.filter(user=value).exists():
            raise serializers.ValidationError("This user already has a doctor profile.")
        return value
        

class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ['id', 'doctor_id', 'date', 'time_slot','status', 'phone_number']     
