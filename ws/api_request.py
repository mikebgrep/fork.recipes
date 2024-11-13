import json
import os

from dotenv import load_dotenv
import requests
from backend import settings
from recipes.models import User

load_dotenv()


# def api_client_read_only():
#     client = RequestsClient()
#     requests.headers['X-AUTH-HEADER'] = os.getenv('X_AUTH_HEADER')
#
#     response = client.get(settings.SERVICE_BASE_URL)
#     client.headers['X-CSRFToken'] = response.cookies['csrftoken']
#
#     return client
#
#
# def api_client_write(token: str):
#     client = RequestsClient()
#     client.headers['Authorization'] = f"Token {token}"
#
#     response = client.get(settings.SERVICE_BASE_URL)
#     client.headers['X-CSRFToken'] = response.cookies['csrftoken']
#
#     return client



def get_user_token(username, password):

    login_data = {
        "username": username,
        "password": password
    }

    headers = {
        'X-Auth-Header': os.getenv('X_AUTH_HEADER')
    }

    response = requests.post(url=settings.SERVICE_BASE_URL + "/api/auth/token", data=login_data, headers=headers)

    if response.status_code == 200:
        user, created =  User.objects.get_or_create(username=username)
        user.token = json.loads(response.content)['token']
        user.save()

        return user
    else:
        return False