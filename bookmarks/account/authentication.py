from django.contrib.auth.backends import BaseBackend

from .models import Profile


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            profile = Profile.objects.get(email=username)
            if profile.check_password(password):
                return profile
            return None
        except (Profile.DoesNotExist, Profile.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        try:
            return Profile.objects.get(pk=user_id)
        except Profile.DoesNotExist:
            return None

