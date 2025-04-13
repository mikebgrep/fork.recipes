from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_view, name='settings_page'),
    path('create', views.create_backup_view, name="create_backup"),
    path('<int:backup_pk>/delete', views.delete_backup_view, name="delete_backup"),
    path('<int:backup_pk>/apply', views.apply_backup_view, name="apply_backup"),

]