import json
import os
from http import HTTPMethod

from dotenv import load_dotenv
import requests
from backend import settings
from recipes.models import User
from types import SimpleNamespace


load_dotenv()


def api_request_read_only(method: str, url: str, data = None):
    headers = {
        'X-Auth-Header': os.getenv('X_AUTH_HEADER')
    }

    response = requests.request(method=method, url=f"{settings.SERVICE_BASE_URL}/{url}", headers=headers, data=data)
    # client.headers['X-CSRFToken'] = response.cookies['csrftoken']

    return response


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

    response = api_request_read_only(method=HTTPMethod.POST, url="api/auth/token", data=login_data)

    if response.status_code == 200:
        user, created = User.objects.get_or_create(username=username)
        user.token = json.loads(response.content)['token']
        user.save()

        return user
    else:
        return False



def get_categories():
    response = api_request_read_only(method=HTTPMethod.GET, url="api/recipe/category")
    results = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    return [x for x in results]


def get_recipes_by_category(category_pk):
    response = api_request_read_only(method=HTTPMethod.GET, url=f"api/recipe/category/{category_pk}/recipes")
    results = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))

    return [x for x in results]

def get_recipes_home(search_query = None, page_number = 1):
    url = f"api/recipe/home/?search={search_query}&page={page_number}" if search_query else f"api/recipe/home/?page={page_number}"
    response = api_request_read_only(method=HTTPMethod.GET, url=url)
    result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))

    return result.count, result.next, result.previous, [x for x in result.results]
