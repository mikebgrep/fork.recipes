import json
import os
from http import HTTPMethod
from typing import List

from dotenv import load_dotenv
import requests
from fork_recipes.backend import settings
from recipes.models import User
from types import SimpleNamespace

from fork_recipes.schedule.models import TIMING_CHOICES

load_dotenv()


def api_request_read_only(method: str, url: str, data=None):
    headers = {
        'X-Auth-Header': os.getenv('X_AUTH_HEADER'),
        'Content-Type': "application/json"
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


def get_user_token(email, password):
    login_data = {
        "email": email,
        "password": password
    }

    response = api_request_read_only(method=HTTPMethod.POST, url="api/auth/token", data=json.dumps(login_data))

    if response.status_code == 200:
        user_response = json.loads(response.content)
        user, created = User.objects.get_or_create(email=email, username=user_response['user']['username'])
        user.token = user_response['token']
        user.save()

        return user
    else:
        return False


def get_categories():
    response = api_request_read_only(method=HTTPMethod.GET, url="api/recipe/category")
    results = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    return results


def get_recipes_by_category(category_pk):
    response = api_request_read_only(method=HTTPMethod.GET, url=f"api/recipe/category/{category_pk}/recipes")
    results = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))

    return results


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
    if response.status_code == 404:
        return False
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


def change_logged_user_password(data: dict, token: str):
    response = api_request_write(method=HTTPMethod.PUT, url="api/auth/user", token=token, data=json.dumps(data))
    if response.status_code == 204:
        return True
    return False


def change_logged_user_username_and_email(data: dict, token: str):
    response = api_request_write(method=HTTPMethod.PATCH, url="api/auth/user", token=token, data=json.dumps(data))
    print(response.content)
    if response.status_code == 200:
        return True
    result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    return result


def delete_user_account(token: str):
    response = api_request_write(method=HTTPMethod.DELETE, url="api/auth/delete-account", token=token)
    if response.status_code == 204:
        return True
    else:
        return False


def request_forgot_password_token(data: dict):
    response = api_request_read_only(method=HTTPMethod.POST, url="api/auth/password_reset", data=json.dumps(data))
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    else:
        return None


def request_change_user_password_on_reset(password_token: str, data: dict):
    response = api_request_read_only(method=HTTPMethod.POST,
                                     url=f"api/auth/password_reset/reset?token={password_token}", data=json.dumps(data))
    print(response.content)
    if response.status_code == 204:
        return True
    if response.status_code == 404:
        return None

    result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    return result


def request_get_profile(token: str):
    response = api_request_write(method=HTTPMethod.GET, url="api/auth/user/info", token=token)
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def request_download_recipe(recipe_url: str, token: str):
    data = {
        "url": recipe_url
    }
    response = api_request_write(method=HTTPMethod.POST, url="api/recipe/scrape", token=token, data=json.dumps(data))
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def request_delete_recipe(recipe_pk: int, token: str):
    response = api_request_write(method=HTTPMethod.DELETE, url=f"api/recipe/{recipe_pk}/", token=token)
    if response.status_code == 204:
        return True

    return False


def reqeust_generate_recipes(ingredients: List[str], token: str):
    data = {
        "ingredients": ingredients
    }
    response = api_request_write(method=HTTPMethod.POST, url="api/recipe/generate", token=token, data=json.dumps(data))
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return True, [x for x in result]
    return False, None


def request_get_schedule_of_a_day(date: str):
    response = api_request_read_only(method=HTTPMethod.GET, url=f"api/schedule/?date={date}")
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def request_post_schedule(date: str, recipe_id: int, timing: TIMING_CHOICES, token: str):
    data = {
        "timing": timing,
        "recipe": recipe_id,
        "date": date
    }
    response = api_request_write(method=HTTPMethod.POST, url="api/schedule/", token=token, data=json.dumps(data))
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def request_get_user_settings(token: str):
    response = api_request_write(method=HTTPMethod.GET, url="api/auth/settings", token=token)
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result
    return None


def request_change_user_settings_language(language_choice: str, token: str):
    data = {
        "language": language_choice
    }

    response = api_request_write(method=HTTPMethod.PATCH, url="api/auth/settings", token=token, data=json.dumps(data))
    if response.status_code == 201:
        return True
    return False


def request_translate_recipe(data: dict, token: str):
    response = api_request_write(method=HTTPMethod.POST, url="api/recipe/translate", token=token, data=json.dumps(data))
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return True, result
    elif response.status_code == 400:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return False, result

    return None, None


def request_get_recipe_variations(recipe_pk: int):
    response = api_request_read_only(method=HTTPMethod.GET, url=f"api/recipe/{recipe_pk}/variations")
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result

    return None


def request_get_list_shopping_lists(token: str):
    response = api_request_write(method=HTTPMethod.GET, url="api/shopping/", token=token)
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result

    return None


def request_delete_shopping_list(list_pk: int, token: str):
    response = api_request_write(method=HTTPMethod.DELETE, url=f"api/shopping/{list_pk}/", token=token)
    if response.status_code == 204:
        return True

    return None


def request_create_shopping_list(name: str, token: str):
    data = {
        "name": name

    }

    response = api_request_write(method=HTTPMethod.POST, url="api/shopping/", data=json.dumps(data), token=token)
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result

    return None


def request_get_shopping_list(list_pk: int, token: str):
    response = api_request_write(method=HTTPMethod.GET, url=f"api/shopping/single/{list_pk}/", token=token)
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result

    return None


def request_update_shopping_list_item(item_pk: int, data: dict, token: str):
    response = api_request_write(method=HTTPMethod.PATCH, url=f"api/shopping/item/{item_pk}/", data=json.dumps(data),
                                 token=token)
    if response.status_code == 200:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result

    return None


def request_add_ingredient_to_shopping_list(list_pk:int, data: dict, token:str):
    response = api_request_write(method=HTTPMethod.PATCH, url=f"api/shopping/single/{list_pk}/", data=json.dumps(data), token=token)
    if response.status_code == 201:
        result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return result

    return None

def request_delete_ingredient_from_shopping_list(item_pk:int, token:str):
    response = api_request_write(method=HTTPMethod.DELETE, url=f"api/shopping/item/{item_pk}/", token=token)
    if response.status_code == 204:
        return True

    return None

def request_complete_shopping_list(list_pk:int, token:str):
    response = api_request_write(method=HTTPMethod.PATCH, url=f"api/shopping/complete-list/{list_pk}/", token=token)
    if response.status_code == 201:
        return True

    return None


def request_complete_single_ingredient(item_pk:int, token:str):
    response = api_request_write(method=HTTPMethod.PATCH, url=f"api/shopping/item/{item_pk}/", token=token)
    if response.status_code == 200:
        return True

    return None