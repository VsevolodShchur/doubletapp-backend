from rest_framework import authentication
from rest_framework import exceptions
from pets import settings


class ApiKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if request.META.get('HTTP_X_API_KEY') != settings.API_KEY:
            raise exceptions.AuthenticationFailed('Invalid Api Key')

    def authenticate_header(self, request):
        return 'Api Key Authentication'
