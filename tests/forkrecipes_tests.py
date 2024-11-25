from datetime import timedelta

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone
from dotenv import load_dotenv
from recipes.models import User
from recipes.views import change_password_after_reset
from recipes.ws import api_request

from .mock_util import *

load_dotenv()



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
    responses_register_mock(responses.POST, path="api/auth/token",
                            json_data={"detail": "No User matches the given query."}, status_code=404)
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
    assert 'recipes/forgot_password_send.html' in [x.name for x in response.templates]


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
    assert "Somethings when wrong. Please try again later or contact administrator!" in [x.message for x in
                                                                                         get_messages(
                                                                                             response.wsgi_request)]
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
    recipe_response, categories_response = mock_categories_and_get_json_response(models.RecipeResponseType.HOME_PREVIEW_PAGINATE)

    responses_register_mock(method=responses.GET, path=f"api/recipe/home/preview/?page=1",
                            json_data=recipe_response, status_code=200)
    api_request.get_recipe_home_preview()
    response = client.get(path=reverse("recipes:recipe_list"))

    assert response.status_code == 200
    assert response.context['selected_category'] == ''
    assert response.context['search_query'] == ''
    assert len(response.context['categories']) == 5


@responses.activate
@pytest.mark.django_db
def test_recipe_list_selected_category(login_with_user, client):
    category_pk = 4
    recipe_response, categories_response = mock_categories_and_get_json_response(models.RecipeResponseType.HOME_PREVIEW_BY_CATEGORY)

    responses_register_mock(method=responses.GET, path=f"api/recipe/category/{category_pk}/recipes",
                            json_data=recipe_response, status_code=200)
    api_request.get_recipes_by_category(category_pk)

    response = client.get(path=reverse("recipes:recipe_list"), data={'category': category_pk})

    assert response.status_code == 200
    assert int(response.context['selected_category']) == category_pk
    assert response.context['search_query'] == ''
    assert len(response.context['categories']) == 5


@responses.activate
@pytest.mark.django_db
def test_recipe_list_view_by_search_query(login_with_user, client):
    recipe_response, categories_response = mock_categories_and_get_json_response(models.RecipeResponseType.HOME_PREVIEW_PAGINATE)

    search_query = "Risotto"
    responses_register_mock(method=responses.GET, path=f"api/recipe/home/preview/?search={search_query}&page=1",
                            json_data=recipe_response, status_code=200)
    api_request.get_recipe_home_preview(search_query)

    response = client.get(path=reverse("recipes:recipe_list"), data={'search': search_query})

    assert response.status_code == 200
    assert response.context['selected_category'] == ''
    assert response.context['search_query'] == search_query
    assert len(response.context['categories']) == 5


@responses.activate
@pytest.mark.django_db
def test_recipe_details_view(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk(client)

    response = client.get(reverse("recipes:recipe_detail", args=[recipe_pk]))

    assert response.status_code == 200
    assert response.context['recipe'].pk == json_response['pk']
    assert response.context['category'].pk == json_response['category']


@responses.activate
@pytest.mark.django_db
def test_edit_recipe_view_get_request(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk(client)
    response = client.get(reverse("recipes:edit_recipe", args=[recipe_pk]))

    assert response.status_code == 200
    assert response.context['recipe'].pk == json_response['pk']
    assert [x.pk for x in response.context['categories']] == [x['pk'] for x in categories_response]
    assert response.context['difficulties'] == DIFFICULTY_CHOICES_CHOICE


@responses.activate
@pytest.mark.django_db
def test_edit_recipe_post_request(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk(client)
    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.PUT, recipe_pk, categories_response, 200)
    response = client.post(reverse("recipes:edit_recipe", args=[recipe_pk]), data=post_data)

    assert response.status_code == 302


@responses.activate
@pytest.mark.django_db
def test_edit_recipe_post_request_bad_request_on_update(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk(client)
    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.PUT, recipe_pk, categories_response, 400)
    response = client.post(reverse("recipes:edit_recipe", args=[recipe_pk]), data=post_data)

    assert response.status_code == 200
    assert "Something went wrong.Try again later" in response.context['message']


@responses.activate
@pytest.mark.django_db
def test_new_recipe_view_happy_path(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk(client)
    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.POST, recipe_pk, categories_response, 201)
    response = client.post(reverse("recipes:new_recipe"), data=post_data)

    assert response.status_code == 302


@responses.activate
@pytest.mark.django_db
def test_new_recipe_view_error_on_request(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk(client)
    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.POST, recipe_pk, categories_response, 400)
    response = client.post(reverse("recipes:new_recipe"), data=post_data)

    assert response.status_code == 200
    assert "Something went wrong.Try again later" in response.context['message']