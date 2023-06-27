from uuid import UUID
from rest_framework_simplejwt.tokens import RefreshToken
import jwt


def is_valid_uuid(uuid):
    try:
        return UUID(uuid).version
    except ValueError:
        return False


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def decode_user_token(token, key, algorithm, options):
    return jwt.decode(
        jwt=token,
        key=key,
        algorithms=['HS256', algorithm],
        options=options
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
