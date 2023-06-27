from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from djchoices import ChoiceItem, DjangoChoices
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from simple_history.models import HistoricalRecords



class STATUS_USER(DjangoChoices):
    Inactive = ChoiceItem(0, 'Inactivo')
    Active = ChoiceItem(1, 'Activo')
    Disabled = ChoiceItem(2, 'Deshabilitado')


class ROL_USER(DjangoChoices):
    Root = ChoiceItem(0, 'Root')
    Admin = ChoiceItem(1, 'Administrador')
    Client = ChoiceItem(2, 'Cliente')


class SEX(DjangoChoices):
    Nonen = ChoiceItem('OO', 'None')
    Feminine = ChoiceItem('F', 'Femenino')
    Male = ChoiceItem('M', 'Masculino')
    NotSayIt = ChoiceItem('X', 'Otro')
    Notbinary = ChoiceItem('Y', 'No Binario')
    Transgenero = ChoiceItem('FTM', 'Transgénero FTM')
    Transgenero = ChoiceItem('MT', 'Transgénero MTF')
    Transaexual = ChoiceItem('MTF', 'Transexual MTF')
    Transaexual = ChoiceItem('FT', 'Transexual FTM')


class CustomUserManager(BaseUserManager):
    """To use email instead of username"""

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    photo = models.ImageField(blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    rol = models.PositiveIntegerField(choices=ROL_USER, null=True, blank=True, default=0)
    birth_date = models.DateField(blank=True, null=True)
    sex = models.CharField(choices=SEX, null=True, blank=True, max_length=3)
    status = models.PositiveIntegerField(choices=STATUS_USER, default=1)
    phone = models.CharField(max_length=50, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    is_email_verified = models.BooleanField(blank=True, null=True, default=False)
    is_phone_verified = models.BooleanField(blank=True, null=True, default=False)
    client = models.ForeignKey('clients.Client', related_name='users_client', on_delete=models.CASCADE, null=True,
                               blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    is_online = models.BooleanField(blank=True, null=True, default=False)
    objects = CustomUserManager()
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name}'

    def generate_token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }