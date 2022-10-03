from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=77, blank=False, default='')
    description = models.CharField(max_length=300, blank=False, default='')
    author = models.CharField(max_length=50, blank=False, default='')
    rating = models.FloatField(blank=False)
    published = models.BooleanField(default=False)


class Auth(models.Model):
    email = models.CharField(max_length=100, blank=False)
    password = models.CharField(max_length=100, blank=False)



class User(AbstractUser):
    first_name = models.CharField(max_length=80, blank=False)
    last_name = models.CharField(max_length=80, blank=False)
    email = models.CharField(max_length=90, blank=False, unique=True)
    username = models.CharField(max_length=80, null=True, blank=False, unique=True)
    password = models.CharField(max_length=90, blank=False)
    # username = None

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
