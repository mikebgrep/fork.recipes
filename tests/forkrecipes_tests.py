import os
from datetime import timedelta

import responses
from django.test import TestCase
from django.utils import timezone
from dotenv import load_dotenv
from recipes.ws import api_request

load_dotenv()


def responses_register_mock(method: responses, path: str, json, status_code: int):
    responses.add(
        method,
        f"{os.getenv('SERVICE_BASE_URL')}/{path}",
        json=json,
        status=status_code,
    )


class TestForkRecipeViews(TestCase):

    @responses.activate
    def test_login_in_login_view(self):
        user_data = {"token": "bba74ec6c4e78d9226bf980cc98bc7177509e279", "user":
            {"username": "user_123", "email": "email@test.com", "is_superuser": True}}

        responses_register_mock(responses.POST, path="api/auth/token", json=user_data, status_code=200)
        api_request.get_user_token("email@test.com", "admin1")

        response = self.client.post(path="/login/", data={"email": user_data['user']['email'], "password": "admin1"})

        self.assertEqual(response.status_code, 302)
        self.assertIn('auth_token', self.client.session)
        self.assertIn('email', self.client.session)

        self.assertEqual(self.client.session['auth_token'], user_data['token'])
        self.assertEqual(self.client.session['email'], user_data['user']['email'])

    @responses.activate
    def test_login_non_existing_user(self):
        responses_register_mock(responses.POST, path="api/auth/token",
                                json={"detail": "No User matches the given query."}, status_code=404)
        api_request.get_user_token("non_existing@test.com", "non_existing")

        response = self.client.post(path="/login/", data={"email": "email@test.com", "password": "admin1"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Wrong email or password!")

    @responses.activate
    def test_login_remember_me_session_time(self):
        user_data = {"token": "bba74ec6c4e78d9226bf980cc98bc7177509e279", "user":
            {"username": "user_123", "email": "email@test.com", "is_superuser": True}}

        responses_register_mock(responses.POST, path="api/auth/token", json=user_data, status_code=200)
        api_request.get_user_token("email@test.com", "admin1")

        response = self.client.post(path="/login/", data={"email": user_data['user']['email'], "password": "admin1",
                                                          "remember-me": True})
        expiry_date = self.client.session.get_expiry_date()
        expected_expiry_date = timezone.now() + timedelta(days=30)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(abs((expiry_date - expected_expiry_date).days) <= 1)

    @responses.activate
    def test_forgot_password_view_user_reset_password(self):
        request_data = {
            "email": "testemail@email.com"
        }
        responses_register_mock(method=responses.POST, path="api/auth/password_reset",
                                json={"token": "bba74ec6c4e78d9226bf980cc98bc7177509e279"}, status_code=201)
        api_request.request_forgot_password_token(request_data)

        response = self.client.post(path="/forgot-password/", data=request_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reset Password Email Send', response.content)
