from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = 'recipes'

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.log_out_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('saved-recipes/', views.saved_recipes, name='saved_recipes'),
    path('profile/', views.profile_view, name='profile'),
    path('toggle-favorite/<int:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('new-recipe/', views.new_recipe, name='new_recipe'),
    path('recipe/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/change-password/', views.change_password, name='change_password'),
    path('settings/update-service-url/', views.update_service_url, name='update_service_url'),
    path('settings/delete-account/', views.delete_account, name='delete_account'),
]
