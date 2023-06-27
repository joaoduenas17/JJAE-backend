from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.utils import datetime_from_epoch
from rest_framework import serializers, exceptions, fields
from users.models import *
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from clients.models import Client
from django.contrib.auth.models import update_last_login
from sorl.thumbnail import get_thumbnail


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super(CustomTokenObtainPairSerializer, self).__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['password'].required = False

    def login_user_registration(self, client, email, password):
        status = 1
        suspended = 0
        expired = 0
        type_valid = 1
        msg = ""
        user = User.objects.filter(client=client, email=email, rol__in=[1, 2], status = 1).first()
        if user:
            if user.username.endswith('-' + client.name.lower()):
                user.username = user.username.replace(
                    '-' + client.name.lower(), '')
        rs = {'status': status, 'suspended': suspended, 'user': user,
              'expired': expired, 'type_valid': type_valid, 'msg': msg}
        return rs

    def login_client_registration(self, client, email):
        status = 1
        suspended = 0
        expired = 0
        type_valid = 1
        msg = ""
        user = User.objects.filter(client=client, email=email, rol__in=[1, 2], status = 1).first()
        if user:
            status = 0
            if user.username.endswith('-' + client.name.lower()):
                user.username = user.username.replace(
                    '-' + client.name.lower(), '')
        else:
            msg = _("Usuario o contraseña incorrectos")
        rs = {'status': status, 'suspended': suspended, 'user': user,
              'expired': expired, 'type_valid': type_valid, 'msg': msg}
        return rs

    def validate(self, attrs):
        request = self.context.get("request", None)
        data = request.data
        email = data.get("email", None)
        password = data.get('password', '')
        code = data.get('code', '')
        id_client = data.get('id_client', None)
        if email or code:
            if id_client:
                client = Client.objects.get(pk=id_client)
            else:
                client = request.client
            setting = client.setting if client else None
            if setting:
                rs = {'status': 1}
                if setting.user_registration or setting.client_registration:

                    if rs['status'] != 0 and setting.user_registration:
                        rs = self.login_user_registration(
                            client, email, password)
                    if rs['status'] != 0 and setting.client_registration:
                        attrs['email'] = email
                        rs = self.login_client_registration(
                            client, email)
                else:
                    msg = "Client settings has not registration property"
                    raise exceptions.AuthenticationFailed(msg)
            else:
                msg = "Client has no configuration"
                raise exceptions.AuthenticationFailed(msg)
            if not rs:
                rs = {}
            status = rs.get('status', 1)
            msg = rs.get('msg', "Error")
            if status == 0:
                user = rs.get('user', None)
                token = self.get_token(user)
                data = super(CustomTokenObtainPairSerializer,
                             self).validate(attrs)
                data['exp'] = token.payload.get(
                    'exp', None) if token is not None else None
                data['user'] = UserSerializer(user).data
                return data
            else:
                raise exceptions.AuthenticationFailed(msg)
        else:
            msg = "email no puede ser none"
            raise exceptions.AuthenticationFailed(msg)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        update_last_login(None, user)
        return token



        return created

class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for create user profile"""
    photo = fields.ImageField(allow_null=True)
    password = serializers.CharField(max_length=128, write_only=True)
    birth_date = serializers.DateField(allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'name', 'last_name', 'photo','rol', 'password', 'birth_date', 'sex', 'phone', 'status',
            'username', 'created_at', 'country', 'postal_code')

    def create(self, validated_data):
        request = self.context.get("request", None)
        validated_data['client'] = request.client


        created = User.objects.create(**validated_data)
        if created:
            created.is_email_verified = True
            created.save()

            if validated_data['password']:
                created.set_password(validated_data['password'])
                created.save()

        return created


class UserSerializer(serializers.ModelSerializer):
    """To retrieve info about an user"""
    rol_name = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'name', 'last_name', 'photo', 'phone', 'rol', 'rol_name',
            'status_name', 'status',  'created_at', 'is_email_verified', 'is_phone_verified', 'country', 
            'postal_code', 'completed')


    def get_type_name(self, instance):
        if instance.type:
            return ROL_USER.values.get(instance.type)
        else:
            return ''

    def get_status_name(self, instance):
        return STATUS_USER.values.get(instance.status)

    def get_rol_name(self, instance):
        return ROL_USER.values.get(instance.rol)

    def get_photo(self, instance):
        if instance.photo:
            thumbnail = get_thumbnail(instance.photo, '70x70', quality=90)
            return thumbnail.url
        else:
            return ''
    
    def get_completed(self, instance):
        if instance.photo:
            return True
        else:
            return False



class UserSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'name', 'last_name', 'email', 'rol')


class PhotoSerializer(serializers.ModelSerializer):
    photo = fields.ImageField(max_length=None, required=True)
    id = serializers.IntegerField(label='id', required=True)

    def create(self, validate_data):
        id = validate_data.get("id", None)
        if id is not None:
            try:
                user = User.objects.get(pk=id)
            except User.DoesNotExist as err:
                detail = {"msg": err, "created": False}
                raise exceptions.NotAcceptable(detail=detail)

            user.photo = validate_data.get("photo")
            user.save()
            return user
        else:
            detail = {"msg": "Something ocurred, try again", "created": False}
            raise exceptions.NotAcceptable(detail=detail)

    class Meta:
        model = User
        fields = ("photo", "id", 'profile_type')


class TokenRefreshSerializer(serializers.Serializer):
    """Copied from rest_framework_simplejwt.serializers.TokenRefreshSerializer.
    Updated/fixed using https://github.com/SimpleJWT/django-rest-framework-simplejwt/issues/25"""
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        data = {'access': str(refresh.access_token)}

        if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
            blacklisted_token = None
            if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION'):
                try:
                    # Attempt to blacklist the given refresh token
                    blacklisted_token, _ = refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            if blacklisted_token:
                OutstandingToken.objects.create(
                    user=blacklisted_token.token.user,
                    jti=refresh.payload['jti'],
                    token=str(refresh),
                    created_at=refresh.current_time,
                    expires_at=datetime_from_epoch(refresh['exp']),
                )

            data['refresh'] = str(refresh)

        return data


class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)  # max_length copied from django.db.models.fields.EmailField

    class Meta:
        fields = ('email',)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            return value
        else:
            raise serializers.ValidationError("There is not user with provided email")


class NewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=128, min_length=8)
    new_password2 = serializers.CharField(max_length=128, min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError('Los valores de contraseña proporcionados no coinciden')
        else:
            return attrs


class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'profile_type')
        extra_kwargs = {
            "email": {"required": True}
        }


class RecoverPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    repeat_password = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['repeat_password']:
            raise serializers.ValidationError("Las contraseñas son diferentes")
        return data

    def create(self, validated_data):
        user = self.context['user']
        password = validated_data.get('password', None)
        if password:
            user.set_password(password)
            user.save()
        return user