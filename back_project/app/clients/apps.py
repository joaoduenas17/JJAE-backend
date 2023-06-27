from django.apps import AppConfig
import os
from django.conf import settings

class ClientsConfig(AppConfig):
    name = 'clients'
    path = os.path.join(settings.BASE_DIR, 'clients')