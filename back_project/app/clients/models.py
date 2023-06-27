import base64
import hashlib
import hmac
import time
from calendar import monthrange
from datetime import date, timedelta

import requests
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Sum
from requests.api import request
from model_utils import Choices
from django.utils.translation import gettext as _
import uuid
import xml.etree.ElementTree as ET
from django.contrib.postgres.fields import ArrayField
import os
from simple_history.models import HistoricalRecords


class ExternalOauth2(models.Model):
    client_id = models.CharField(max_length=100, blank=True, default='')
    scope = models.CharField(max_length=100,  blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    redirect_uri = models.URLField(null=True, blank=True, default='')
    grant_type = models.CharField(max_length=100, blank=True, default='')
    endpoint = models.URLField(null=True, blank=True, default='')
    endpoint_user_info = models.URLField(null=True, blank=True, default='')
    authorize_endpoint = models.URLField(null=True, blank=True, default='')
    endpoint_logout = models.URLField(null=True, blank=True, default='')
    secret_id = models.CharField(max_length=100,  blank=True, default='')

    class Meta:
        verbose_name_plural = 'Externals oauth2'

    def __str__(self):
        return self.client_id


class WebService(models.Model):
    reference = models.CharField(max_length=50, blank=True)
    endpoint = models.URLField()
    endpoint_details = models.URLField(default="", blank=True)
    method = models.CharField(max_length=10, blank=True)
    field_id = models.CharField(max_length=25)
    field_pass = models.CharField(max_length=25)
    field_detail = models.CharField(max_length=150, blank=True)


    def verify_authenticate_bibliotheca(self, username, password):
        api_url = self.endpoint
        account_id = self.field_id
        account_key = self.field_pass
        url = api_url 
        utc = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime())
        data_to_sign = utc + "\n" + "GET" + "\n" 
        message = bytes(data_to_sign, 'utf-8')
        secret = bytes(account_key, 'utf-8')
        signature = base64.b64encode(
            hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode()
        authorization = '3MCLAUTH ' + account_id + ':' + signature
        headers = {'3mcl-Datetime': utc, '3mcl-Authorization': authorization}
        response = requests.get(url, headers=headers)
        root = ET.fromstring(response.content)
        result = root[0].text
        reason = ''
        status = 1
        if result == 'SUCCESS':
            status = 0
        else:
            reason = result
        result = {'status': status, 'msg': reason}
        return result

    def __str__(self):
        return self.reference

    class Meta:
        verbose_name_plural = "Web services"



class Setting(models.Model):
    CARRUSEL_TYPE = Choices(
        (1, 'DEFAULT', _('Default')),
        (2, 'REDUCED', _('Reducido'))
    )
    MENU_STYLE = Choices(
        (1, 'DEFU', _('Default')),
        (2, 'THES', _('The shelf'))
    )
    PLATAFORM_TYPE = Choices(
        (1, 'UNIQ', _('Unique')),
        (2, 'MULT', _('Multiple'))
    )
    carrusel_type = models.IntegerField(choices=CARRUSEL_TYPE, default=1)
    menu_style = models.IntegerField(choices=MENU_STYLE, default=1)
    plataform_type = models.IntegerField(choices=PLATAFORM_TYPE, default=1)
    has_chat = models.BooleanField(default=False)
    has_streaming = models.BooleanField(default=False)
    show_date_renovation = models.BooleanField(default=False)
    has_sso = models.BooleanField(default=False)
    has_redirect = models.BooleanField(default=False)
    user_registration = models.BooleanField(default=False)
    client_registration = models.BooleanField(default=False)
    external_registration = models.BooleanField(default=False)

    def __str__(self):
        name = ''
        try:
            client = self.client
            name = client.name
        except:
            pass
        return name


class Client(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(
        upload_to='logos', null=True, blank=True, default='')
    logo_menu = models.ImageField(
        upload_to='logos', null=True, blank=True, default='')
    logo_footer = models.ImageField(
        upload_to='logos', null=True, blank=True, default='')
    url_web = models.URLField(null=True, blank=True, default='')
    email = models.EmailField()
    province = models.CharField(max_length=50)
    town = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    owner = models.CharField(max_length=255, blank=True, null=True)
    platform_name = models.CharField(max_length=255, blank=True, null=True)
    setting = models.OneToOneField(
        Setting, null=True, related_name='client', on_delete=models.CASCADE)
    web_service = models.ForeignKey(
        WebService, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    sites = models.ManyToManyField(Site, related_name='clients')
    client_login_id = models.UUIDField(default=uuid.uuid4, editable=True)
    has_web = models.BooleanField(default=True)
    has_app = models.BooleanField(default=False)
    update_client_status = models.BooleanField(default=False)
    oauth2_external = models.ForeignKey(
        ExternalOauth2, null=True, blank=True, default=None, on_delete=models.SET_NULL
    )
    has_own_style = models.BooleanField(default=False)
    unsubscribe_msg = models.CharField(max_length=2000, blank=True, null=True)
    default_coins_user = models.IntegerField(default=0)


    @property
    def accepted_users(self):
        """get accepted users"""
        from users.models import User
        result = self.users.filter(status=User.STATUS.ACCEPTED)
        return result

    @property
    def number_accepted_users(self):
        """get number of accepted users"""
        result = self.accepted_users.count()
        return result

    @property
    def waiting_users(self):
        """get waiting users"""
        from users.models import User
        result = self.users.filter(status=User.STATUS.WAITING)
        return result

    @property
    def number_waiting_users(self):
        """get number of waiting users"""
        result = self.waiting_users.count()
        return result

    @property
    def rejected_users(self):
        """get rejected users"""
        from users.models import User
        result = self.users.filter(status=User.STATUS.REJECTED)
        return result

    @property
    def number_rejected_users(self):
        """get number of rejected users"""
        result = self.rejected_users.count()
        return result

    def __str__(self):
        return self.name




class FAQ(models.Model):
    question = models.CharField(max_length=200, blank=False)
    response = models.TextField(blank=False, max_length=1000)
    is_generic = models.BooleanField(default=False)
    clients = ArrayField(models.CharField(
        max_length=100, blank=True, null=True), blank=True, default=list)
    order = models.IntegerField(default=0)
    PRODUCT_TYPE = Choices(
        (1, 'MOVIES', _('Movies')),
        (2, 'MAGAZINES', _('Magazines')),
        (2, 'GENERICS', _('Generics'))
    )
    product_type = models.IntegerField(
        choices=PRODUCT_TYPE, default=PRODUCT_TYPE.MOVIES)



class ClientFAQ(models.Model):
    order = models.IntegerField(default=0)
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)



class SocialNetwork(models.Model):
    TYPE = Choices(
        (1, 'FACEBOOK', 'Facebook'),
        (2, 'TWITTER', 'Twitter'),
        (3, 'INSTAGRAM', 'Instagram'),
        (4, 'YOUTUBE', 'Youtube')
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    url = models.URLField(default='', blank=True)
    type = models.IntegerField(choices=TYPE, default=TYPE.FACEBOOK)
    active = models.BooleanField(default=True)
    icon = models.ImageField(upload_to='icons')



class TextGeneralCondition(models.Model):
    text = models.TextField()
    client = models.ForeignKey(
        Client, related_name='general_conditions', null=True, blank=True, on_delete=models.CASCADE)



class TextTermsCondition(models.Model):
    text = models.TextField()
    client = models.ForeignKey(
        Client, related_name='terms_conditions', null=True, blank=True, on_delete=models.CASCADE)




class SingleColor(models.Model):
    image = models.ImageField(upload_to='images')
    color = models.CharField(max_length=15, null=True, blank=True)
    color_name = models.CharField(max_length=35, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)



class NewsLetterSubscription(models.Model):
    email = models.EmailField(
        max_length=70, null=False, blank=False, unique=True)

    class Meta:
        verbose_name_plural = 'New letter Subscriptions'

    def __str__(self):
        return self.email
