from drf_yasg import openapi

auth_header = openapi.Parameter('Authentication', openapi.IN_HEADER, description="JWT access_token_value",
                                required=True, type=openapi.TYPE_STRING)