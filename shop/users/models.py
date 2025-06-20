from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=100)
    is_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20)

    class Meta:
        db_table = "users"
        
    def __str__(self):
        return f"{self.name} ({self.email})"