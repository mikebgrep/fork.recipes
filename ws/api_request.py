import json
import os
from http import HTTPMethod

from dotenv import load_dotenv
import requests
from backend import settings
from recipes.models import User
from types import SimpleNamespace

load_dotenv()


def api_request_read_only(method: str, url: str, data=None):
    headers = {
        'X-Auth-Header': os.getenv('X_AUTH_HEADER')
    }

    response = requests.request(method=method, url=f"{settings.SERVICE_BASE_URL}/{url}", headers=headers, data=data)
    return response


def api_request_write(method: str, url: str, token: str, data=None, files=None):
    headers = {
        'Authorization': f"Token {token}",
    }
    if files is None:
        headers['Content-Type'] = "application/json"

    response = requests.request(method=method, url=f"{settings.SERVICE_BASE_URL}/{url}", headers=headers, data=data,
                                files=files)
    return response


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


# TODO:// To be deleted
def get_recipes_home(search_query=None, page_number=1):
    url = f"api/recipe/home/?search={search_query}&page={page_number}" if search_query else f"api/recipe/home/?page={page_number}"
    response = api_request_read_only(method=HTTPMethod.GET, url=url)
    result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))

    return result.count, result.next, result.previous, [x for x in result.results]


def get_recipe_home_preview(search_query=None, page_number=1):
    url = f"api/recipe/home/preview/?search={search_query}&page={page_number}" if search_query else f"api/recipe/home/preview/?page={page_number}"

    response = api_request_read_only(method=HTTPMethod.GET, url=url)
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result.count, result.next, result.previous, [x for x in result.results]

    return 0, None, None, []


def get_recipe_by_pk(pk: int):
    response = api_request_read_only(HTTPMethod.GET, url=f"api/recipe/{pk}/")
    result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    return result


def patch_favorite_recipe(pk: int, token: str):
    response = api_request_read_only(method=HTTPMethod.PATCH, url=f"api/recipe/{pk}/favorite")
    return response.status_code


def get_favorite_recipes(page_number=1):
    response = api_request_read_only(method=HTTPMethod.GET, url=f"api/recipe/home/favorites/?page={page_number}")
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result.count, result.next, result.previous, [x for x in result.results]

    return 0, None, None, []


def post_category(token: str, data: dict):
    response = api_request_write(method=HTTPMethod.POST, url="api/recipe/category/add", token=token,
                                 data=json.dumps(data))
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def post_new_recipe_main_info(multipart_form_data: dict, files: list, token: str):
    response = api_request_write(method=HTTPMethod.POST, url="api/recipe/", token=token, data=multipart_form_data,
                                 files=files)
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def post_ingredients_for_recipe(recipe_pk: int, token: str, data: list):
    response = api_request_write(method=HTTPMethod.POST, url=f"api/recipe/{recipe_pk}/ingredients", token=token,
                                 data=json.dumps(data))
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def post_instructions_for_recipe(recipe_pk: int, token: str, data: list):
    response = api_request_write(method=HTTPMethod.POST, url=f"api/recipe/{recipe_pk}/steps", token=token,
                                 data=json.dumps(data))
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def update_recipe_main_info(recipe_pk: int, multipart_form_data: dict, files: list, token: str):
    response = api_request_write(method=HTTPMethod.PUT, url=f"api/recipe/{recipe_pk}", token=token,
                                 data=multipart_form_data,
                                 files=files)
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None
