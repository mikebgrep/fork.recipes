import json
import os

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from fork_recipes.ws import api_request
from recipes.models import LANGUAGES_CHOICES


@login_required
def settings_view(request):
    token = request.session.get("auth_token")
    user_settings = api_request.request_get_user_settings(token=token)
    languages = [choice[0] for choice in LANGUAGES_CHOICES if
                 choice[0] != user_settings.preferred_translate_language]

    backups = api_request.request_get_backups(token)

    processed_backups = []
    if backups:
        processed_backups = [{"file": backup.file.split('/')[-1], "pk": backup.pk} for backup in backups]

    context = {
        'languages': languages,
        'selected_language': user_settings.preferred_translate_language,
        'backups': processed_backups,
        'user_settings': user_settings,
    }

    return render(request, 'settings.html', context=context)


@login_required
def change_translation_language(request):
    if request.method == 'POST':
        language_choice = request.POST.get("language_choice")
        token = request.session.get("auth_token")
        response = api_request.request_change_user_settings(token, language_choice)
        if response:
            messages.success(request, 'Your translation language was successfully updated!')
            return redirect('settings:settings_page')


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


@login_required
def apply_backup_view(request, backup_pk):
    token = request.session.get("auth_token")

    is_applied = api_request.request_apply_backup(backup_pk, token)
    if is_applied:
        messages.success(request, f'Backup was successfully applied.')
        user = request.user
        logout(request)
        user.delete()
    else:
        messages.error(request, f'There was an error processing the backup request.Please try again.')
    logout(request)
    return redirect("recipes:login")


@login_required
def import_backup_file_view(request):
    token = request.session.get("auth_token")

    if request.method == "POST":
        backup_file = request.FILES.get('backup_file')
        backup_file = [("file", backup_file)]
        is_uploaded = api_request.reqeust_import_backup(backup_file, token)

        if is_uploaded:
            messages.success(request, f'Backup was successfully imported.')
        else:
            messages.error(request, f'There was an error processing the backup request.Please try again.')


    return redirect("settings:settings_page")

@login_required
def export_backup_file_view(request, backup_pk):
    token = request.session.get("auth_token")
    backup = api_request.request_get_backup(backup_pk, token)

    if backup.file:
        file_path = f"settings/data/{backup.file.split('/')[-1]}"
        import urllib.request
        urllib.request.urlretrieve(backup.file, file_path)
        try:
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        finally:
            os.remove(file_path)

    messages.error(request, f'There was an error processing the backup download request.Please try again.')
    return redirect("settings:settings_page")


@login_required
def enable_emojy_in_ingredients_on_scrape(request):
    pass


@login_required
def enable_compact_pdf(request):
    if request.method == "POST":
        token = request.session.get("auth_token")
        data = json.loads(request.body)
        enabled = data.get('enabled')
        is_success = api_request.request_change_user_settings(token=token, compact_pdf=enabled)

        return JsonResponse({'status': 'success' if is_success else "failure"})


@login_required
def enable_emoji_recipes(request):
    if request.method == "POST":
        token = request.session.get("auth_token")
        data = json.loads(request.body)
        enabled = data.get('enabled')

        is_success = api_request.request_change_user_settings(token=token, emoji_recipes=enabled)
        return JsonResponse({'status': 'success' if is_success else "failure"})
