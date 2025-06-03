from django.urls import path, include
from users.views import UserView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserView, basename='user')

urlpatterns = [] + router.urls


