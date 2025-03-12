from django.contrib import admin
from .models import User, Doctor, Bookings

admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Bookings)