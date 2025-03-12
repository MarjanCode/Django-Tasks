from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return self.email


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    available_slots = models.JSONField(default=list)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctors'

    def __str__(self):
        return f"{self.name} ({self.specialty})"
    
     
class Bookings(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
        
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
    
    def __str__(self):
        return f"Booking {self.id} - {self.patient.email} with Dr. {self.doctor.name} on {self.date} at {self.time_slot}"
    
