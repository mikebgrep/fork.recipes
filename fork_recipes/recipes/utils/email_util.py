from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from fork_recipes.backend import settings


def send_reset_password_link(host, user_email, reset_password_token):
    context = {
        'user_email': user_email,
        'base_url': settings.SERVICE_BASE_URL,
        'support_url': "support@forkrecipes.com",
        'action_url': "{}reset?token={}".format(
            host,
            reset_password_token)
    }

    # render email text
    email_html_message = render_to_string('email/reset_password.html', context)

    msg = EmailMultiAlternatives(
        # title:
        "Reset password request for Fork Recipes account.",
        # message:
        "Password reset token",
        # from
        "noreplay@forkrecipes.com",
        # to:
        [user_email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


def check_smtp_configuration():
    required_settings = [
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_USE_TLS",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
    ]

    missing_settings = [
        setting for setting in required_settings if not getattr(settings, setting, None)
    ]

    if missing_settings:
        return False, f"Missing SMTP configuration settings: {', '.join(missing_settings)} in environment variables!"

    return True, "SMTP is properly configured."
