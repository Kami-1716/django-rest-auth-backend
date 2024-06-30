import jwt
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import Auth0User

class Auth0JSONWebTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return None

        parts = auth.split()

        if parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Authorization header must start with Bearer')
        elif len(parts) == 1:
            raise exceptions.AuthenticationFailed('Token not found')
        elif len(parts) > 2:
            raise exceptions.AuthenticationFailed('Authorization header must be Bearer token')

        token = parts[1]
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        rsa_key = self._get_rsa_key(unverified_header)
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=['RS256'],
                    audience=settings.AUTH0_AUDIENCE,
                    issuer=settings.AUTH0_ISSUER_BASE_URL
                )
            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Token has expired')
            except jwt.InvalidTokenError:
                raise exceptions.AuthenticationFailed('Invalid token')
            except jwt.PyJWTError as e:
                raise exceptions.AuthenticationFailed(f'Error decoding token: {str(e)}')

            auth0_id = payload.get('sub')
            user, created = Auth0User.objects.get_or_create(auth0Id=auth0_id)

            # Set auth0_id and user_id on the request object
            request.auth0_id = auth0_id
            request.user_id = user.id

            return (user, token)

        raise exceptions.AuthenticationFailed('Unable to find appropriate key')

    def _get_rsa_key(self, unverified_header):
        jwks_url = f"{settings.AUTH0_ISSUER_BASE_URL}.well-known/jwks.json"
        response = requests.get(jwks_url)
        jwks = response.json()

        rsa_key = None
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not rsa_key:
            raise exceptions.AuthenticationFailed('Unable to find appropriate key')

        return rsa_key
