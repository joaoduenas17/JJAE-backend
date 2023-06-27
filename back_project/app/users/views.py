from rest_framework.exceptions import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser, FileUploadParser
from rest_framework import status
from django_filters import rest_framework as filters
from users.utils import get_client_ip
from users.filters import UserFilter
from users.models import *
from users.serializers import CustomTokenObtainPairSerializer, RegisterUserSerializer, \
    UserSerializer, UserSmallSerializer,  PhotoSerializer, UserEmailSerializer, NewPasswordSerializer, ForgotPasswordSerializer, \
    RecoverPasswordSerializer
from users.schemas import RespLogin, RespRefreshToken
from commons.pagination import StandardPagination
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from users.tokens import account_activation_token
from django.core.mail import send_mail
from django.db.models import Q, F
from django.contrib.auth import logout
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.template.loader import render_to_string


class AuthTokenViewSet(TokenObtainPairView):

    def get_serializer_class(self):
        has_refresh = self.request.data.get('refresh', False)
        return CustomTokenObtainPairSerializer if not has_refresh else TokenRefreshSerializer


class UserViewSet(ModelViewSet):
    parser_classes = (JSONParser, MultiPartParser, FormParser,)
    pagination_class = StandardPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = UserFilter
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = User.objects.filter(client=self.request.client)
        return queryset.order_by('-id')

    def get_serializer_class(self):
        if self.action in ['create']:
            return RegisterUserSerializer
        else:
            return UserSerializer

    @action(methods=['patch'], detail=True, url_path="update-user", url_name="update-user")
    def update_user(self, request, pk=None):
        try:
            user = self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            content = {
                "message": "User not found",
                "id": pk,
                "error": True
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterUserSerializer(
            user, data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userData = User.objects.filter(id=pk).first()
        serializerUser = UserSerializer(userData)
        content = {
            "message": "updated successfully",
            "data": serializerUser.data,
            "updated": True
        }

        return Response(content, status=status.HTTP_200_OK)

    @action(methods=['delete'], detail=True, url_path="delete-user", url_name="delete-user")
    def delete_user(self, request, pk=None):
        try:
            user = self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            content = {
                "message": "User not found",
                "id": pk,
                "error": True
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        user.status = 2
        user.save()
        content = {
            "message": "deleted successfully",
        }
        return Response(content, status=status.HTTP_200_OK)

    @swagger_auto_schema(without_auth=True, request_body=RegisterUserSerializer,
                         responses={'201': UserSerializer, '400': 'Object with error information'})
    def post(self, request):
        ser = RegisterUserSerializer(data=request.data, context={'request': request})
        if ser.is_valid():
            user = ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        user = request.user
        user.is_online = False
        user.save()
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path="get-info", url_name="get-info",
            permission_classes=[IsAuthenticated])
    def get_info(self, request):
        user = request.user
        if (user.rol == 0):
            user.client = request.client
            user.is_email_verified = True
            user.name = user.first_name
            user.rol = ROL_USER.Client
            user.status = STATUS_USER.Active
            user.save()

        refresh = RefreshToken.for_user(user)
        response = UserSerializer(user)
        newResponse = {'refresh': str(refresh), 'access': str(refresh.access_token), }
        newResponse.update(response.data)
        return Response(newResponse, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path="photo-upload", url_name="photo-upload")
    def photo_upload(self, request, pk=None):
        serializer = PhotoSerializer(data=request.data)
        serializer.is_valid(True)
        serializer.save()
        response = {
            "msg": "Logo created",
            "created": True
        }
        return Response(response, status=status.HTTP_201_CREATED)
    
    @action(methods=['get'], detail=False, url_path="verification-user", url_name="verification-user")
    def verification_user(self, request):
        email = request.query_params.get("email", None)
        try:
            user = User.objects.filter(email=email).values("id").first()
            if user:
                return Response(user, status=status.HTTP_200_OK)
            else:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(None, status=status.HTTP_400_BAD_REQUEST)


class CustomJWT(TokenObtainPairView):
    """For login. Customized to return specific data"""
    user_serializer_class = UserSerializer
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(without_auth=True,
                         responses={'200': RespLogin,
                                    '401': '{"error": "No active account found with the given credentials"}'})
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.filter(email=request.data['email'], rol__in=[2, 3, 4]).first()
            if user:
                serialized_user = self.user_serializer_class(user)
                response.data.update(serialized_user.data)
            else:
                return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        return response


class CustomRefreshTokenView(TokenRefreshView):
    """Create to fix issue 25 in django-rest-framework-simplejwt"""
    serializer_class = TokenRefreshSerializer

    @swagger_auto_schema(without_auth=True,
                         responses={'200': RespRefreshToken,
                                    '401': '{"detail": "Token is invalid or expired", "code": "token_not_valid"}'})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ResetPasswordView(ModelViewSet):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser,)

    @action(methods=['post'], detail=False, serializer_class=ForgotPasswordSerializer, url_path='forgot-password',
            url_name='forgot-password')
    def forgot_password(self, request):
        email = request.data.get('email')
        meta = request.META.get("HTTP_ORIGIN", "localhost:8000")
        if meta[-1] == '/':
            meta = meta[:-1]
        user = User.objects.filter(Q(email=email), is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            msg_email = request.client.name + ' <' + request.client.email + '>'
            ip = get_client_ip(request)
            context = ({"name": user.name, "email": user.email,
                        "url": request.client.url_web + 'changePassword/' + uid + '/' + token, "ip": ip,
                        "unsubscribe_msg": ""})
            html_content = render_to_string('reset_password_email.html', context, request=request)
            send_mail('Recupera tu contraseña', html_content, msg_email, [user.email], html_message=html_content)
            content = {
                "message": "Para recuperar su password siga las indicaciones enviadas a su mail",
                "error": False
            }
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {
                "message": "El correo electrónico, no se encuentra registrado",
                "error": True
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['post'], detail=False, url_name='recover-password', url_path='recover-password')
    def recover_password(self, request):
        uid = request.query_params['uid']
        token = request.query_params['token']
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            serializer = RecoverPasswordSerializer(
                data=request.data, context={'user': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            content = {
                "message": "La contraseña fue cambiada exitosamente",
                "error": False
            }
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {
                "message": "El enlace no es válido",
                "error": True
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path="change-password", url_name="change-password")
    def change_password(self, request):
        ser = NewPasswordSerializer(data=request.data)
        if ser.is_valid():
            new_passw = ser.validated_data['new_password']
            user = request.user
            user.set_password(new_passw)
            user.save()
            return Response('Password changed successfully', status=status.HTTP_200_OK)
        else:
            if ser.errors['new_password'][0].code == 'password_too_common':
                return Response({'new_password': [
                    ErrorDetail(string='Esta contraseña es demasiado común. ', code='password_too_common')]},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

