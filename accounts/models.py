from django.db import models

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPES = [
        ('regular', 'Regular User'),
        ('enthusiast', 'Sneaker Enthusiast'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='regular')

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

