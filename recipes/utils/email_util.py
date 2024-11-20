from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.core.mail import send_mail

from backend import settings


def get_connection_temp():
    connection = get_connection(
        backend='django.core.mail.backends.smtp.EmailBackend',
        host= settings.EMAIL_HOST_TEMP,
        port= settings.EMAIL_PORT_TEMP,
        username= settings.EMAIL_HOST_USER_TEMP,
        password= settings.EMAIL_HOST_PASSWORD_TEMP,
        use_tls=True,
    )
    return connection



def send_test_email_to_user_after_change_smtp(user_email):
    msg = EmailMultiAlternatives(
        # title:
        "This is test email from Fork Recipes instance",
        # message:
        "SMTP settings was set.You can request password reset link if you forgot your password and can't login into the app.",
        # from
        "noreplay@forkrecipes.com",
        # to:
        [user_email],

        connection=get_connection_temp()
    )

    msg.send()


def send_reset_password_link(host, user_email, reset_password_token):
    context = {
        'user_email': user_email,
        'base_url': settings.SERVICE_BASE_URL,
        'action_url': "{}/forgot-password/reset?token={}".format(
            host,
            reset_password_token)
    }

    # render email text
    email_html_message = render_to_string('email/reset_password.html', context)

    msg = EmailMultiAlternatives(
        # title:
        "This is test email from Fork Recipes instance",
        # message:
        "Password reset token",
        # from
        "noreplay@forkrecipes.com",
        # to:
        [user_email],
        connection=get_connection_temp()
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()