from django.contrib import admin
from .models import User, Doctor, Booking

admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Booking)