import os, json
import random
import uuid
from http import HTTPMethod

import responses
from . import models
from fork_recipes.ws import api_request
from recipes.models import DIFFICULTY_CHOICES

DIFFICULTY_CHOICES_CHOICE = [choice[0] for choice in DIFFICULTY_CHOICES]

with open('tests/payload.json', 'r') as file:
    json_data_responses = json.load(file)


def get_new_password_data_and_token():
    new_password = f"password-{uuid.uuid4()}"
    request_password_data = {
        "password": new_password,
        "confirm_password": new_password
    }
    token = uuid.uuid4()

    return request_password_data, token


def responses_register_mock(method: responses, path: str, status_code: int, json_data=None):
    responses.add(
        method,
        f"{os.getenv('SERVICE_BASE_URL')}/{path}",
        json=json_data,
        status=status_code,
    )


def mock_token_user():
    json_response = json_data_responses['responses']['authentication']['user_login_success']
    responses_register_mock(responses.POST, path="api/auth/token", json_data=json_response, status_code=200)

    return json_response


def mock_login_user_not_found():
    json_response = json_data_responses['responses']['authentication']['user_not_found']
    responses_register_mock(responses.POST, path="api/auth/token",
                            json_data=json_response, status_code=404)

    api_request.get_user_token("non_existing@test.com", "non_existing")


def mock_forgot_password_success():
    json_response = json_data_responses['responses']['authentication']['password_reset_success']
    responses_register_mock(method=responses.POST, path="api/auth/password_reset", json_data=json_response,
                            status_code=201)


def mock_forgot_password_forbidden():
    json_response = json_data_responses['responses']['authentication']['password_reset_forbidden']
    responses_register_mock(method=responses.POST, path="api/auth/password_reset",
                            json_data=json_response, status_code=403)


def mock_change_password_after_reset():
    request_password_data, token = get_new_password_data_and_token()
    responses_register_mock(method=responses.POST, path=f"api/auth/password_reset/reset?token={token}",
                            status_code=204)

    return token, request_password_data


def mock_change_password_after_reset_token_does_not_match():
    json_response = json_data_responses['responses']['authentication']['password_reset_token_does_not_match']
    request_password_data, token = get_new_password_data_and_token()

    responses_register_mock(method=responses.POST, path=f"api/auth/password_reset/reset?token={token}",
                            json_data=json_response,
                            status_code=404)

    return request_password_data, token


def mock_get_recipe_by_pk():
    json_response, categories_response = mock_categories_and_get_recipes_response(
        models.RecipeResponseType.RECIPE_DETAILS)
    recipe_pk = json_response['pk']
    responses_register_mock(method=responses.GET, path=f"api/recipe/{recipe_pk}/", json_data=json_response,
                            status_code=200)

    return json_response, recipe_pk, categories_response


def mock_post_recipe_ingredients(recipe_pk: int):
    response_data = json_data_responses['responses']['ingredients']
    responses_register_mock(method=responses.POST, path=f"api/recipe/{recipe_pk}/ingredients", status_code=201,
                            json_data=response_data)

    return response_data


def mock_post_recipe_instructions(recipe_pk: int):
    response_data = json_data_responses['responses']['steps']
    responses_register_mock(method=responses.POST, path=f"api/recipe/{recipe_pk}/steps", status_code=201,
                            json_data=response_data)

    return response_data


def mock_create_update_recipe_full_info(method: HTTPMethod, status_code: int):
    response_recipe = json_data_responses['responses']['recipes']['recipe_details']
    response_data = response_recipe if status_code != 400 else {
        "category": ["Incorrect type. Expected pk value, received str."]}

    match method:
        case HTTPMethod.POST:
            responses_register_mock(method=responses.POST, path=f"api/recipe/", status_code=status_code,
                                    json_data=response_data)
        case HTTPMethod.PUT:
            responses_register_mock(method=responses.PUT, path=f"api/recipe/{response_recipe['pk']}",
                                    status_code=status_code,
                                    json_data=response_data)

    ingredients_response_data = mock_post_recipe_ingredients(response_recipe['pk'])
    instructions_response_data = mock_post_recipe_instructions(response_recipe['pk'])

    return response_data, ingredients_response_data, instructions_response_data


def mock_data_recipe_on_update_or_create(method: HTTPMethod, recipe_pk, categories_response, status_code: int):
    post_data = {
        "name": f"name-{uuid.uuid4()}",
        "category": categories_response[0]['pk'],
        "difficulty": random.choice(DIFFICULTY_CHOICES_CHOICE),
        "prep_time": int(random.uniform(20, 60)),
        "cook_time": int(random.uniform(10, 60)),
        "servings": int(random.uniform(1, 10)),
        "description": f"Description-{uuid.uuid4()}",
        "chef": f"Chef-{uuid.uuid4()}",
        "ingredient_name[]": ['ingredient-1', 'ingredient-4', 'ingredient-3'],
        "ingredient_quantity[]": ['10', '20', '30'],
        "ingredient_metric[]": ["pcs", "tbs", "tps"],
        "instructions[]": [f"Instruction-{uuid.uuid4()}", f"Instruction-{uuid.uuid4()}"],
        "clear_video": False
    }

    recipe_main_info_data = {
        "name": post_data['name'],
        "category": post_data['category'],
        "difficulty": post_data['difficulty'],
        "prep_time": post_data['prep_time'],
        "cook_time": post_data['cook_time'],
        "servings": post_data['servings'],
        "description": post_data['description'],
        "chef": post_data['chef'],
        "is_favorite": True
    }

    recipe_files = [
        ("image", open("tests/uploads/upload-image.png", 'rb')),
        ("video", open("tests/uploads/upload-video.mp4", 'rb'))
    ]

    ingredients_data = []
    for name, quantity, metric in zip(post_data["ingredient_name[]"], post_data['ingredient_quantity[]'],
                                      post_data['ingredient_metric[]']):
        ingredients_data.append({"name": name, "quantity": quantity, "metric": metric})

    instructions_data = []
    for instruction in post_data['instructions[]']:
        instructions_data.append({"text": instruction})

    mock_create_update_recipe_full_info(method, status_code)
    generate_token = uuid.uuid4()

    match method:
        case HTTPMethod.PUT:
            api_request.update_recipe_main_info(recipe_pk, multipart_form_data=recipe_main_info_data,
                                                files=recipe_files, token=generate_token)
        case HTTPMethod.POST:
            api_request.post_new_recipe_main_info(multipart_form_data=recipe_main_info_data, files=recipe_files,
                                                  token=generate_token)

    api_request.post_ingredients_for_recipe(recipe_pk, token=generate_token, data=ingredients_data)
    api_request.post_instructions_for_recipe(recipe_pk, token=generate_token, data=instructions_data)

    return post_data


def mock_categories_and_get_recipes_response(recipe_response_type: models.RecipeResponseType):
    categories_response = json_data_responses['responses']['categories']

    responses_register_mock(method=responses.GET, path=f"api/recipe/category",
                            json_data=categories_response,
                            status_code=200)

    api_request.get_categories()
    recipe_response = {}

    match recipe_response_type:
        case models.RecipeResponseType.HOME_PREVIEW_PAGINATE:
            recipe_response = json_data_responses['responses']['recipes']['search_recipes']['home_paginate']
            responses_register_mock(method=responses.GET, path=f"api/recipe/home/preview/?page=1",
                                    json_data=recipe_response, status_code=200)

        case models.RecipeResponseType.HOME_PREVIEW_BY_CATEGORY:
            recipe_response = json_data_responses['responses']['recipes']['search_recipes']['home_by_category']
            category_pk = categories_response[0]['pk']
            responses_register_mock(method=responses.GET,
                                    path=f"api/recipe/category/{category_pk}/recipes",
                                    json_data=recipe_response, status_code=200)
        case models.RecipeResponseType.RECIPE_DETAILS:
            recipe_response = json_data_responses['responses']['recipes']['recipe_details']

    return recipe_response, categories_response


def mock_get_user_profile_request():
    profile_response = json_data_responses['responses']['profile_info']['success']
    responses_register_mock(method=responses.GET, path="api/auth/user/info", json_data=profile_response,
                            status_code=200)

    return profile_response


def mock_change_user_profile_info_success():
    profile_response = mock_get_user_profile_request()

    request_data = {
        "username": profile_response['username'],
        "email": profile_response['email'],
    }

    responses_register_mock(method=responses.PATCH, path="api/auth/user", json_data=profile_response, status_code=200)

    return profile_response, request_data


def mock_change_user_profile_info_bad_request():
    profile_response = json_data_responses['responses']['profile_info']['bad_request']
    responses_register_mock(method=responses.PATCH, path="api/auth/user", json_data=profile_response, status_code=400)
    get_profile_response = mock_get_user_profile_request()

    return profile_response, get_profile_response


def mock_get_favorite_recipes(page_number: int):
    json_response = json_data_responses['responses']['recipes']['favorite_recipes']
    responses_register_mock(responses.GET, path=f"api/recipe/home/favorites/?page={page_number}",
                            json_data=json_response, status_code=200)

    return json_response


def mock_favorite_action_recipe(recipe_pk, status_code: int):
    responses_register_mock(method=responses.PATCH, path=f"api/recipe/{recipe_pk}/favorite", status_code=status_code)


def mock_change_password_from_settings(status_code: int):
    json_request = json_data_responses['requests']['authentication']['change_password_logged_user_success']
    data = json_data_responses['requests']['authentication']['change_password_success']

    responses_register_mock(responses.PUT, path="api/auth/user", status_code=status_code)

    return data, json_request


def mock_delete_account(status_code: int):
    responses_register_mock(responses.DELETE, path="api/auth/delete-account", status_code=status_code)

def mock_get_user_settings():
    json_response = json_data_responses['responses']['user_profile']['user_settings']
    responses_register_mock(method=responses.GET, path="api/auth/settings", json_data=json_response, status_code=200)
