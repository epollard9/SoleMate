from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class CalendarEntry(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to='shoe_images/', blank=True, null=True)