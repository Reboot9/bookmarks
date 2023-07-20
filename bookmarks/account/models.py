from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, AbstractUser
from django.db import models


class Contact(models.Model):
    """Model that determines user subscriptions to other users"""
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


class Profile(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    following = models.ManyToManyField('self', through=Contact,
                                       related_name='followers', symmetrical=False
                                       )

    def __str__(self):
        return f"Profile of {self.username}"
