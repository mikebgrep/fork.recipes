from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from fork_recipes.ws import api_request
from recipes.models import LANGUAGES_CHOICES


@login_required
def settings_view(request):
    token = request.session.get("auth_token")
    user_settings = api_request.request_get_user_settings(token=token)
    languages = [choice[0] for choice in LANGUAGES_CHOICES if
                 choice[0] != user_settings.preferred_translate_language]
    backups = api_request.request_get_backups(token)
    processed_backups = [{"file": backup.file.split('/')[-1], "pk": backup.pk}  for backup in backups]

    context = {
        'languages': languages,
        'selected_language': user_settings.preferred_translate_language,
        'backups': processed_backups,
    }

    return render(request, 'settings.html', context=context)


@login_required
def create_backup_view(request):
    token = request.session.get("auth_token")

    is_created = api_request.request_create_backup(token)
    if is_created:
        messages.success(request, f'Backup was successfully created.')
    else:
        messages.error(request, f'There was an error processing the backup request.Please try again.')

    return redirect("settings:settings_page")


@login_required
def delete_backup_view(request, backup_pk):
    token = request.session.get("auth_token")
    is_deleted = api_request.reqeust_delete_backup(backup_pk, token)
    if is_deleted:
        messages.success(request, f'Backup was successfully deleted.')
    else:
        messages.error(request, f'There was an error processing the backup request.Please try again.')

    return redirect("settings:settings_page")


def apply_backup_view(request, backup_pk):
    token = request.session.get("auth_token")

    is_applied = api_request.request_apply_backup(backup_pk, token)
    if is_applied:
        messages.success(request, f'Backup was successfully applied.')
    else:
        messages.error(request, f'There was an error processing the backup request.Please try again.')

    return redirect("settings:settings_page")