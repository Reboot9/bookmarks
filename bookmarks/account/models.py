from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import models


class Profile(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f"Profile of {self.username}"
