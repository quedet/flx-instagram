from django.contrib.auth.backends import BaseBackend

from .models import User
from apps.core.utils import is_valid_email


class AuthenticationBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        identifier = kwargs.get('username')
        password = kwargs.get('password')

        try:
            if is_valid_email(identifier):
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(username=identifier)

            if user.check_password(password):
                return user
            return None

        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
