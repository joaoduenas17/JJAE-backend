from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import IsAuthenticated
from django.urls import re_path

URL_API_BASE = 'api/v1/'

schema_view = get_schema_view(
    openapi.Info(title="Hermanas Tierra API", default_version='v1', description="API for Hermanas Tierra project"),
    public=True,
    permission_classes=(IsAuthenticated,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path('swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path('redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path(URL_API_BASE, include(('clients.urls', 'clients'), namespace='clients')),
    path(URL_API_BASE, include(('users.urls', 'users'), namespace='users')),
   
    path(URL_API_BASE + 'accounts/', include('allauth.urls')),

]

urlpatterns += [
    re_path(r'^ht/', include('health_check.urls')),
]
