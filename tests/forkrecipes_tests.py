import random
from datetime import timedelta
from http.client import responses

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone
from dotenv import load_dotenv
from recipes.models import User
from recipes.views import change_password_after_reset
from fork_recipes.ws import api_request
from recipes.utils import date_util

from .mock_util import *

load_dotenv()


@pytest.fixture
def login_with_user(client):
    user, created = User.objects.get_or_create(username="test_user", email="test@email.com", token=uuid.uuid4())
    client.force_login(user)
    session = client.session
    session['email'] = "test@email.com"
    session.save()

@responses.activate
@pytest.mark.django_db
def test_login_in_login_view(client):
    user_data = mock_token_user()
    api_request.get_user_token("email@test.com", "admin1")
    response = client.post(reverse("recipes:login"), data={"email": user_data['user']['email'], "password": "admin1"})

    assert response.status_code == 302
    assert 'auth_token' in client.session
    assert 'email' in client.session
    assert client.session['auth_token'] == user_data['token']
    assert client.session['email'] == user_data['user']['email']


@responses.activate
def test_login_non_existing_user(client):
    mock_login_user_not_found()
    response = client.post(reverse("recipes:login"), data={"email": "email@test.com", "password": "admin1"})

    assert response.status_code == 200
    assert response.context['message'] == "Wrong email or password!"


@pytest.mark.django_db
def test_login_view_with_authorized_user_redirect(login_with_user, client):
    response = client.get(reverse("recipes:login"))
    assert response.status_code == 302


@responses.activate
@pytest.mark.django_db
def test_login_remember_me_session_time(client):
    user_data = mock_token_user()
    api_request.get_user_token("email@test.com", "admin1")
    response = client.post(reverse("recipes:login"), data={"email": user_data['user']['email'], "password": "admin1",
                                                           "remember-me": True})
    expiry_date = client.session.get_expiry_date()
    expected_expiry_date = timezone.now() + timedelta(days=30)

    assert response.status_code == 302
    assert abs((expiry_date - expected_expiry_date).days) <= 1


@pytest.mark.django_db
def test_log_out_view(login_with_user, client):
    response = client.get(reverse("recipes:logout"), follow=True)

    assert response.status_code == 200
    assert type(response.context['user']) is AnonymousUser


@responses.activate
def test_forgot_password_view_user_reset_password(client):
    """
        This test should have smtp vars set in .env file.Keep in mine if its failing
    """
    mock_forgot_password_success()
    json_request = json_data_responses['requests']['authentication']['password_reset_json']
    api_request.request_forgot_password_token(json_request)

    response = client.post(reverse("recipes:forgot_password"), data=json_request)

    assert response.status_code == 200
    print(response.context)
    assert b'Reset Password Email Send' in response.content
    assert 'recipes/forgot_password_send.html' in [x.name for x in response.templates]


@pytest.mark.django_db
def test_forgot_password_view_redirect_for_login_user(login_with_user, client):
    response = client.get(reverse("recipes:forgot_password"))

    assert response.status_code == 302


@responses.activate
def test_forgot_password_forbidden_on_request(client):
    """
        This test should have smtp vars set in .env file.Keep in mine if its failing
    """
    mock_forgot_password_forbidden()
    json_request = json_data_responses['requests']['authentication']['password_reset_json']
    api_request.request_forgot_password_token(json_request)

    response = client.post(reverse("recipes:forgot_password"), data=json_request)

    assert response.status_code == 200
    assert "Somethings when wrong. Please try again later or contact administrator!" in [x.message for x in
                                                                                         get_messages(
                                                                                             response.wsgi_request)]
    assert 'recipes/forgot_password.html' in [x.name for x in response.templates]


@responses.activate
@pytest.mark.django_db
def test_change_password_after_reset(client):
    token, request_data = mock_change_password_after_reset()
    api_request.request_change_user_password_on_reset(token, request_data)

    client.get(path=f"/forgot-password/reset?token={token}")
    response = client.post(path="/forgot-password/reset", data=request_data)

    assert response.status_code == 302
    assert "Password was successfully reset." in [x.message for x in get_messages(response.wsgi_request)]
    assert response.resolver_match.func == change_password_after_reset


@responses.activate
@pytest.mark.django_db
def test_change_password_after_reset_token_does_not_match(client):
    request_data, token = mock_change_password_after_reset_token_does_not_match()
    api_request.request_change_user_password_on_reset(token, request_data)

    client.get(path=f"/forgot-password/reset?token={token}")
    response = client.post(path="/forgot-password/reset", data=request_data)

    assert response.status_code == 200
    assert "The provided token does match the query." in [x.message for x in get_messages(response.wsgi_request)]
    assert response.resolver_match.func == change_password_after_reset


@responses.activate
@pytest.mark.django_db
def test_recipe_list_view_response(login_with_user, client):
    recipe_response, categories_response = mock_categories_and_get_recipes_response(
        models.RecipeResponseType.HOME_PREVIEW_PAGINATE)
    api_request.get_recipe_home_preview()
    api_request.get_recipe_home_preview()
    response = client.get(path=reverse("recipes:recipe_list"))

    assert response.status_code == 200
    assert response.context['selected_category'] == ''
    assert response.context['search_query'] == ''
    assert len(response.context['categories']) == len(categories_response)


@responses.activate
@pytest.mark.django_db
def test_recipe_list_selected_category(login_with_user, client):
    recipe_response, categories_response = mock_categories_and_get_recipes_response(
        models.RecipeResponseType.HOME_PREVIEW_BY_CATEGORY)
    category_pk = categories_response[0]['pk']
    api_request.get_recipes_by_category(category_pk)

    response = client.get(path=reverse("recipes:recipe_list"), data={'category': category_pk})

    assert response.status_code == 200
    assert int(response.context['selected_category']) == category_pk
    assert response.context['search_query'] == ''
    assert len(response.context['categories']) == 5


@responses.activate
@pytest.mark.django_db
def test_recipe_list_view_by_search_query(login_with_user, client):
    recipe_response, categories_response = mock_categories_and_get_recipes_response(
        models.RecipeResponseType.HOME_PREVIEW_PAGINATE)

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
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk()
    api_request.get_recipe_by_pk(recipe_pk)
    mock_get_shopping_list()
    api_request.request_get_shopping_lists(str(uuid.uuid4()))

    response = client.get(reverse("recipes:recipe_detail", args=[recipe_pk]))

    assert response.status_code == 200
    assert response.context['recipe'].pk == json_response['pk']
    assert response.context['recipe'].image == json_response['image']
    assert response.context['recipe'].name == json_response['name']
    assert response.context['recipe'].chef == json_response['chef']
    assert response.context['recipe'].video == json_response['video']
    assert response.context['recipe'].description == json_response['description']
    assert response.context['category'].pk == json_response['category']['pk']


@responses.activate
@pytest.mark.django_db
def test_edit_recipe_view_get_request(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk()
    response = client.get(reverse("recipes:edit_recipe", args=[recipe_pk]))

    assert response.status_code == 200
    assert response.context['recipe'].pk == json_response['pk']
    assert [x.pk for x in response.context['categories']] == [x['pk'] for x in categories_response]
    assert response.context['difficulties'] == DIFFICULTY_CHOICES_CHOICE


@responses.activate
@pytest.mark.django_db
def test_edit_recipe_post_request(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk()
    mock_patch_recipe_category()
    api_request.get_recipe_by_pk(recipe_pk)

    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.PUT, recipe_pk, categories_response, 200)
    response = client.post(reverse("recipes:edit_recipe", args=[recipe_pk]), data=post_data)

    assert response.status_code == 302


@responses.activate
@pytest.mark.django_db
def test_edit_recipe_post_request_bad_request_on_update(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk()
    api_request.get_recipe_by_pk(recipe_pk)

    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.PUT, recipe_pk, categories_response, 400)
    response = client.post(reverse("recipes:edit_recipe", args=[recipe_pk]), data=post_data)

    assert response.status_code == 200
    assert "Something went wrong.Try again later" in response.context['message']


@responses.activate
@pytest.mark.django_db
def test_new_recipe_view_happy_path(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk()
    mock_patch_recipe_category()
    api_request.get_recipe_by_pk(recipe_pk)

    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.POST, recipe_pk, categories_response, 201)
    response = client.post(reverse("recipes:new_recipe"), data=post_data)

    assert response.status_code == 302


@responses.activate
@pytest.mark.django_db
def test_new_recipe_view_error_on_request(login_with_user, client):
    json_response, recipe_pk, categories_response = mock_get_recipe_by_pk()
    api_request.get_recipe_by_pk(recipe_pk)
    post_data = mock_data_recipe_on_update_or_create(HTTPMethod.POST, recipe_pk, categories_response, 400)
    response = client.post(reverse("recipes:new_recipe"), data=post_data)

    assert response.status_code == 200
    assert "Something went wrong.Try again later" in response.context['message']


@responses.activate
@pytest.mark.django_db
def test_profile_view_get_request(login_with_user, client):
    profile_response = mock_get_user_profile_request()
    token = uuid.uuid4()
    api_request.request_get_profile(token)

    response = client.get(reverse("recipes:profile"))

    assert response.status_code == 200
    assert response.context['user']['username'] == profile_response['username']
    assert response.context['user']['email'] == profile_response['email']
    assert response.context['user']['date_joined'] == date_util.format_date_joined(profile_response['date_joined'])


@responses.activate
@pytest.mark.django_db
def test_profile_view_post_request(login_with_user, client):
    profile_response, request_data = mock_change_user_profile_info_success()
    token = uuid.uuid4()
    api_request.change_logged_user_username_and_email(request_data, token)

    response = client.post(reverse("recipes:profile"), data=request_data)
    assert response.status_code == 200
    assert response.context['user']['username'] == profile_response['username']
    assert response.context['user']['email'] == profile_response['email']
    assert response.context['user']['date_joined'] == date_util.format_date_joined(profile_response['date_joined'])


@responses.activate
@pytest.mark.django_db
def test_profile_view_post_request_bad_request_on_api(login_with_user, client):
    profile_response, request_data = mock_change_user_profile_info_bad_request()
    token = uuid.uuid4()
    api_request.change_logged_user_username_and_email(request_data, token)

    response = client.post(reverse("recipes:profile"), data=request_data)

    assert response.status_code == 200
    assert "This email address already exists or is invalid.Please choice another." in [x.message for x in get_messages(
        response.wsgi_request)]


@responses.activate
@pytest.mark.django_db
def test_saved_recipes_view(login_with_user, client):
    current_page_number = 1
    json_response = mock_get_favorite_recipes(current_page_number)
    api_request.get_favorite_recipes(current_page_number)

    response = client.get(reverse("recipes:saved_recipes"))

    assert response.status_code == 200
    recipe_pagination = response.context['page_obj']
    assert len(recipe_pagination) == 2
    assert [x['pk'] for x in json_response['results']] == [recipe_pagination[0].pk, recipe_pagination[1].pk]


@responses.activate
@pytest.mark.django_db
def test_toggle_favorite_success(login_with_user, client):
    recipe_pk = int(random.uniform(1, 100))
    mock_favorite_action_recipe(recipe_pk, status_code=201)
    api_request.patch_favorite_recipe(recipe_pk, uuid.uuid4())

    response = client.post(reverse("recipes:toggle_favorite", args=[recipe_pk]))
    assert response.status_code == 200
    assert "success" == response.json()['status']


@responses.activate
@pytest.mark.django_db
def test_toggle_favorite_bad_request(login_with_user, client):
    recipe_pk = int(random.uniform(1, 100))
    mock_favorite_action_recipe(recipe_pk, status_code=400)
    api_request.patch_favorite_recipe(recipe_pk, token=str(uuid.uuid4()))

    response = client.post(reverse("recipes:toggle_favorite", args=[recipe_pk]))
    assert response.status_code == 200
    assert "failure" == response.json()['status']



@responses.activate
@pytest.mark.django_db
def test_change_password_settings_happy_path(login_with_user, client):
    data, json_request = mock_change_password_from_profile(status_code=204)
    mock_get_user_profile_request()
    api_request.change_logged_user_password(data=data, token=str(uuid.uuid4()))

    mock_get_user_settings()
    api_request.request_get_user_settings(token=str(uuid.uuid4()))

    response = client.post(reverse("recipes:change_password"), data=json_request, follow=True)
    assert response.status_code == 200
    assert 'recipes/profile.html' in [t.name for t in response.templates]
    assert 'Your password was successfully updated!' in [x.message for x in get_messages(response.wsgi_request)]


@responses.activate
@pytest.mark.django_db
def test_change_password_settings_passwords_does_not_match(login_with_user, client):
    json_request = json_data_responses['requests']['authentication'][
        'change_password_logged_user_passwords_does_not_match']

    mock_get_user_settings()
    api_request.request_get_user_settings(token=str(uuid.uuid4()))

    response = client.post(reverse("recipes:change_password"), data=json_request)

    assert response.status_code == 200
    assert 'recipes/profile.html' in [t.name for t in response.templates]
    assert 'Please correct the error below.' in [x.message for x in get_messages(response.wsgi_request)]
    assert 'Your new password does not match confirm password!' == response.context['error']


@responses.activate
@pytest.mark.django_db
def test_change_password_api_bad_request(login_with_user, client):
    data, json_request = mock_change_password_from_profile(status_code=400)
    api_request.change_logged_user_password(data=data, token=str(uuid.uuid4()))

    mock_get_user_settings()
    api_request.request_get_user_settings(token=str(uuid.uuid4()))

    response = client.post(reverse("recipes:change_password"), data=json_request)

    assert response.status_code == 200
    assert 'Please correct the error below.' in [x.message for x in get_messages(response.wsgi_request)]
    assert 'There problem with your new password. Please choice minimum 8 char long password and not to common.' == \
           response.context['error']


@responses.activate
@pytest.mark.django_db
def test_settings_delete_account_happy_path(login_with_user, client):
    token = uuid.uuid4()
    mock_delete_account(status_code=204)
    api_request.delete_user_account(token)

    mock_get_user_settings()
    api_request.request_get_user_settings(token=str(uuid.uuid4()))

    response = client.post(reverse("recipes:delete_account"), follow=True)

    assert response.status_code == 200
    assert client.session['auth_token'] is None
    assert 'recipes/login.html' in [t.name for t in response.templates]
    assert 'Your account has been successfully deleted.' in [x.message for x in get_messages(response.wsgi_request)]

    with pytest.raises(User.DoesNotExist):
        User.objects.get(email='test@email.com')


@responses.activate
@pytest.mark.django_db
def test_settings_delete_account_api_no_creds_provided(login_with_user, client):
    mock_delete_account(status_code=403)
    mock_get_user_profile_request()
    api_request.delete_user_account(None)

    mock_get_user_settings()
    api_request.request_get_user_settings(token=str(uuid.uuid4()))

    response = client.post(reverse("recipes:delete_account"), follow=True)

    assert response.status_code == 200
    assert 'recipes/profile.html' in [t.name for t in response.templates]
    assert 'Something went wrong.Please try again later!' in [x.message for x in get_messages(response.wsgi_request)]


@responses.activate
@pytest.mark.django_db
def test_settings_delete_account_api_bad_request(login_with_user, client):
    mock_delete_account(status_code=500)
    mock_get_user_profile_request()
    api_request.delete_user_account(None)

    mock_get_user_settings()
    api_request.request_get_user_settings(token=str(uuid.uuid4()))

    response = client.post(reverse("recipes:delete_account"), follow=True)

    assert response.status_code == 200
    assert 'recipes/profile.html' in [t.name for t in response.templates]
    assert 'Something went wrong.Please try again later!' in [x.message for x in get_messages(response.wsgi_request)]
