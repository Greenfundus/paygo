from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class BearerAuthentication(TokenAuthentication):
    keyword = 'Bearer'

