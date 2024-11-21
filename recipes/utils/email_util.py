from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.core.mail import send_mail

from backend import settings




def send_reset_password_link(host, user_email, reset_password_token):
    context = {
        'user_email': user_email,
        'base_url': settings.SERVICE_BASE_URL,
        'support_url': "support@forkrecipes.com",
        'action_url': "http://{}/forgot-password/reset?token={}".format(
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
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()