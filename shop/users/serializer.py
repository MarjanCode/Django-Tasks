from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "phone_number", "is_seller"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
