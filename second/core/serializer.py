from rest_framework import serializers
from .models import User, Doctor, Booking
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
        fields = ['id', 'name', 'specialty', 'available_slots']

    def validate_user(self, value):
        if Doctor.objects.filter(user=value).exists():
            raise serializers.ValidationError("This user already has a doctor profile.")
        return value
    
    def update(self, instance, validated_data):
        new_slots = validated_data.pop('available_slots', [])
        instance.available_slots.extend(new_slots)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
        

class BookingSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField()
    
    class Meta:
        model = Booking
        fields = ['id', 'doctor_id', 'date', 'time_slot', 'status']     
