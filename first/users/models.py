from django.db import models

class User(models.Model):
    email = models.EmailField(max_length = 254, unique=True)
    password = models.CharField(max_length=255)
    created_time = models.DateTimeField(auto_now_add=True)

