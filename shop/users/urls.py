from django.urls import path, include
from users.views import UserSignupView, UserView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserView, basename='user')


urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
] + router.urls