# middlewares.py

from django.utils.deprecation import MiddlewareMixin

class Auth0IdInjectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(request, 'auth0_id') and hasattr(request, 'user_id'):
            request.user.auth0_id = request.auth0_id
            request.user.user_id = request.user_id
