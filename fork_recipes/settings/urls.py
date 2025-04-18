from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_view, name='settings_page'),
    path('create', views.create_backup_view, name="create_backup"),
    path('<int:backup_pk>/delete', views.delete_backup_view, name="delete_backup"),
    path('<int:backup_pk>/apply', views.apply_backup_view, name="apply_backup"),
    path('import', views.import_backup_file_view, name="import_backup"),
    path('<int:backup_pk>/export', views.export_backup_file_view, name="export_backup"),
    path('change-translation-language/', views.change_translation_language, name="change_translation_language"),
    path('change-pdf-option/', views.enable_compact_pdf, name="compact_pdf"),
    path('emoji-recipes-option/', views.enable_compact_pdf, name="emoji_recipes")

]