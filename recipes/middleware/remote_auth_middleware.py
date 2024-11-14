# myapp/middleware/remote_auth_middleware.py

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
import requests

User = get_user_model()


class RemoteAuthenticationMiddleware(MiddlewareMixin):

    """
    Class for authentication of the user if the SESSION_COOKIE_AGE value from settings.py
    expire the user is logged out.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            return

        token = request.session.get('auth_token')
        if not token:
            request.user = AnonymousUser()
            return
