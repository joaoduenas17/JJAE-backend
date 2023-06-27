import requests
from requests.exceptions import ConnectionError, TooManyRedirects, Timeout
import logging
from users.models import User

logger = logging.getLogger('django')
logger.setLevel(logging.INFO)


class HttpMethods:
    @staticmethod
    def get(url, headers={}):
        try:
            return requests.get(url, headers=headers)
        except (ConnectionError, TooManyRedirects, Timeout, ) as error:
            logger.info("connection error")
            logger.info(error)
        except requests.exceptions.HTTPError as error:
            logger.info("api request get")
            logger.info(error)

    @staticmethod
    def post(url, payload, is_json, headers={}):
        try:
            return requests.post(url, json=payload, headers=headers) if is_json\
                else requests.post(url, data=payload, headers=headers)
        except (ConnectionError, TooManyRedirects, Timeout, ) as error:
            logger.info("connection error")
            logger.info(error)
        except requests.exceptions.HTTPError as error:
            logger.info("api request get")
            logger.info(error)


def add_user_oauth(username, email, client):
    user, created = User.objects.get_or_create(
        username=username,
        email=email,
        defaults={
            'profile': 2,
            'client': client,
            'status': 1
        }
    )
    if created:
        user.set_password('')
        user.save()
    return user
