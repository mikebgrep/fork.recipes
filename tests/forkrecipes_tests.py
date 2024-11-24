import json
import os
import uuid
from datetime import timedelta
from wsgiref.validate import assert_

import pytest
import responses
from django.test import TestCase
from django.utils import timezone
from dotenv import load_dotenv
from recipes.ws import api_request
from recipes.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from recipes.views import login_view, change_password_after_reset

load_dotenv()


def responses_register_mock(method: responses, path: str, status_code: int, json_data=None):
    responses.add(
        method,
        f"{os.getenv('SERVICE_BASE_URL')}/{path}",
        json=json_data,
        status=status_code,
    )


def mock_categories_and_get_json_response(is_category_list: bool = False):
    responses_register_mock(method=responses.GET, path=f"api/recipe/category",
                            json_data='[{"pk":1,"name":"Breakfast"},{"pk":2,"name":"Lunch"},{"pk":3,"name":"Sunday"},\
                                          {"pk":4,"name":"Pizza"},{"pk":5,"name":"Brunch"}]',
                            status_code=200)

    api_request.get_categories()
    preview_response = {"count": 1, "next": None,
                        "previous": None,
                        "results": [{"pk": 46,
                                     "image": "http://localhost:8000/media/images/8ddef70f-dd9d-44b1-847f-834cdf97e7bd_d5122d74-1c5e-40d3-a505-f9d09383d1ba_delicio_X3L8djK.jpg",
                                     "name": "Creamy Mushroom Risotto", "chef": "Julia Child", "servings": 1,
                                     "total_time": 1.62,
                                     "difficulty": "Intermediate", "is_favorite": False}]}

    preview_response_list = [{"pk": 46,
                              "image": "http://localhost:8000/media/images/8ddef70f-dd9d-44b1-847f-834cdf97e7bd_d5122d74-1c5e-40d3-a505-f9d09383d1ba_delicio_X3L8djK.jpg",
                              "name": "Creamy Mushroom Risotto", "chef": "Julia Child", "servings": 1,
                              "total_time": 1.62,
                              "difficulty": "Intermediate", "is_favorite": False}]

    return preview_response_list if is_category_list else preview_response


@pytest.fixture
def login_with_user(client):
    user, created = User.objects.get_or_create(username="test_user", email="test@email.com", token=uuid.uuid4())
    client.force_login(user)


@responses.activate
@pytest.mark.django_db
def test_login_in_login_view(client):
    user_data = {"token": "bba74ec6c4e78d9226bf980cc98bc7177509e279", "user":
        {"username": "user_123", "email": "email@test.com", "is_superuser": True}}

    responses_register_mock(responses.POST, path="api/auth/token", json_data=user_data, status_code=200)
    api_request.get_user_token("email@test.com", "admin1")

    response = client.post(path="/login/", data={"email": user_data['user']['email'], "password": "admin1"})

    assert response.status_code == 302
    assert 'auth_token' in client.session
    assert 'email' in client.session

    assert client.session['auth_token'] == user_data['token']
    assert client.session['email'] == user_data['user']['email']


@responses.activate
def test_login_non_existing_user(client):
    responses_register_mock(responses.POST, path="api/auth/token", json_data={"detail": "No User matches the given query."}, status_code=404)
    api_request.get_user_token("non_existing@test.com", "non_existing")

    response = client.post(path="/login/", data={"email": "email@test.com", "password": "admin1"})

    assert response.status_code == 200
    assert response.context['message'] == "Wrong email or password!"

@responses.activate
@pytest.mark.django_db
def test_login_remember_me_session_time(client):
    user_data = {"token": "bba74ec6c4e78d9226bf980cc98bc7177509e279", "user":
        {"username": "user_123", "email": "email@test.com", "is_superuser": True}}

    responses_register_mock(responses.POST, path="api/auth/token", json_data=user_data, status_code=200)
    api_request.get_user_token("email@test.com", "admin1")

    response = client.post(path="/login/", data={"email": user_data['user']['email'], "password": "admin1",
                                                      "remember-me": True})
    expiry_date = client.session.get_expiry_date()
    expected_expiry_date = timezone.now() + timedelta(days=30)

    assert response.status_code == 302
    assert abs((expiry_date - expected_expiry_date).days) <= 1

@responses.activate
def test_forgot_password_view_user_reset_password(client):
    request_data = {
        "email": "testemail@email.com"
    }
    responses_register_mock(method=responses.POST, path="api/auth/password_reset",
                            json_data={"token": "bba74ec6c4e78d9226bf980cc98bc7177509e279"}, status_code=201)
    api_request.request_forgot_password_token(request_data)

    response = client.post(path="/forgot-password/", data=request_data)

    assert response.status_code == 200
    assert b'Reset Password Email Send' in response.content
    assert  'recipes/forgot_password_send.html' in [x.name for x in response.templates]

@responses.activate
def test_forgot_password_forbidden_on_request(client):
    request_data = {
        "email": "testemail@email.com"
    }
    responses_register_mock(method=responses.POST, path="api/auth/password_reset",
                            json_data={"detail": "You must use authentication header"}, status_code=403)
    api_request.request_forgot_password_token(request_data)

    response = client.post(path="/forgot-password/", data=request_data)

    assert response.status_code == 200
    assert "Somethings when wrong. Please try again later or contact administrator!" in [x.message for x in get_messages(response.wsgi_request)]
    assert 'recipes/forgot_password.html' in [x.name for x in response.templates]

@responses.activate
@pytest.mark.django_db
def test_change_password_after_reset(client):
    new_password = f"password-{uuid.uuid4()}"
    request_data = {
        "password": new_password,
        "confirm_password": new_password
    }
    token = uuid.uuid4()

    responses_register_mock(method=responses.POST, path=f"api/auth/password_reset/reset?token={token}",
                            status_code=204)
    api_request.request_change_user_password_on_reset(token, request_data)
    client.get(path=f"/forgot-password/reset?token={token}")
    response = client.post(path="/forgot-password/reset", data=request_data)

    assert response.status_code == 302
    assert "Password was successfully reset." in [x.message for x in get_messages(response.wsgi_request)]
    assert response.resolver_match.func == change_password_after_reset

@responses.activate
@pytest.mark.django_db
def test_change_password_after_reset_token_does_not_match(client):
    new_password = f"password-{uuid.uuid4()}"
    request_data = {
        "password": new_password,
        "confirm_password": new_password
    }
    token = uuid.uuid4()

    responses_register_mock(method=responses.POST, path=f"api/auth/password_reset/reset?token={token}",
                            json_data='{"detail":"No PasswordResetToken matches the given query."}}',
                            status_code=404)
    api_request.request_change_user_password_on_reset(token, request_data)
    client.get(path=f"/forgot-password/reset?token={token}")
    response = client.post(path="/forgot-password/reset", data=request_data)

    assert response.status_code == 200
    assert "The provided token does match the query." in [x.message for x in get_messages(response.wsgi_request)]
    assert response.resolver_match.func == change_password_after_reset

@responses.activate
@pytest.mark.django_db
def test_recipe_list_view_response(login_with_user, client):
    json_response = mock_categories_and_get_json_response()

    responses_register_mock(method=responses.GET, path=f"api/recipe/home/preview/?page=1",
                            json_data=json_response, status_code=200)
    api_request.get_recipe_home_preview()
    response = client.get(path=reverse("recipes:recipe_list"))

    assert  response.status_code == 200
    assert  response.context['selected_category'] == ''
    assert  response.context['search_query'] == ''
    assert len(json.loads(response.context['categories'])) == 5

@responses.activate
@pytest.mark.django_db
def test_recipe_list_selected_category(login_with_user, client):
    category_pk = 4
    preview_response = mock_categories_and_get_json_response(is_category_list=True)

    responses_register_mock(method=responses.GET, path=f"api/recipe/category/{category_pk}/recipes",
                            json_data=preview_response, status_code=200)
    api_request.get_recipes_by_category(category_pk)

    response = client.get(path=reverse("recipes:recipe_list"), data={'category': category_pk})

    assert response.status_code == 200
    assert int(response.context['selected_category']) == category_pk
    assert response.context['search_query'] == ''
    assert len(json.loads(response.context['categories'])) == 5

@responses.activate
@pytest.mark.django_db
def test_recipe_list_view_by_search_query(login_with_user, client):
    json_response = mock_categories_and_get_json_response()

    search_query = "Risotto"
    responses_register_mock(method=responses.GET, path=f"api/recipe/home/preview/?search={search_query}&page=1",
                            json_data=json_response, status_code=200)
    api_request.get_recipe_home_preview(search_query)

    response = client.get(path=reverse("recipes:recipe_list"), data={'search': search_query})

    assert response.status_code == 200
    assert response.context['selected_category'] == ''
    assert response.context['search_query'] == search_query
    assert len(json.loads(response.context['categories'])) == 5
