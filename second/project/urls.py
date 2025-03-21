"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import signup, login, DoctorProfileAPIView, BookAppointmentAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/signup/', signup),
    path('api/v1/login/', login),
    path('api/v1/doctors/', DoctorProfileAPIView.as_view()),
    path('api/v1/doctors/<int:doctor_id>/', DoctorProfileAPIView.as_view(), name='delete-slot'),
    path('api/v1/appointments/', BookAppointmentAPIView.as_view(), name='create-appointment'),
    path('api/v1/appointments/<int:booking_id>/', BookAppointmentAPIView.as_view(), name='manage-appointment'),
]

