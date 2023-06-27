from django.utils import translation
from django.contrib.sites.models import Site
from django.http import HttpResponseNotFound
from clients.models import Client
from rest_framework_simplejwt import authentication
from users.utils import is_valid_uuid
import user_agents
import logging
logger = logging.getLogger('django')
logger.setLevel(logging.INFO)


class GetClientMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not path.startswith('/api'):
            request.empresa = None
            response = self.get_response(request)
            return response
        client_id = request.META.get('HTTP_CLIENT_ID', None)
        logger.info(client_id)
        origin = request.META.get('HTTP_ORIGIN', None)
        user = None
        try:
            user = authentication.JWTAuthentication().authenticate(request)
        except:
            logger.info(
                'error obteniendo el token de autenticacion middleware')
            pass
        if user is not None:
            try:
                request.client = user[0].client
            except:
                logger.info(
                    'error obteniendo el cliente desde el user')
                pass
            response = self.get_response(request)
            return response
        elif client_id and is_valid_uuid(client_id):
            client = Client.objects.filter(client_login_id=client_id).first()
            logger.info('client')
            logger.info(client)
            request.client = client
            response = self.get_response(request)
            return response
        elif origin:
            origins = origin.split('//')
            if len(origins) > 1:
                origin = origins[1]
            site = Site.objects.filter(domain=origin).first()
        else:
            site = Site.objects.get_current(request)
        if site:
            client = site.clients.first()
            if client:
                request.client = client
                response = self.get_response(request)
                return response
            else:
                return HttpResponseNotFound('Usuario o contraseña incorrectos.')
        else:
            return HttpResponseNotFound('Usuario o contraseña incorrectos.')


class LocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not path.startswith('/api'):
            request.empresa = None
            response = self.get_response(request)
            return response
        language = translation.get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        response = self.get_response(request)
        return response

    def process_request(self, request):
        language = translation.get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        translation.deactivate()
        return response
