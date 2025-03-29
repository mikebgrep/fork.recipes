from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:recipe_pk>/', views.recipe_detail, name='recipe_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.log_out_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-password/reset', views.change_password_after_reset, name='change_password_after_reset'),

    path('saved-recipes/', views.saved_recipes, name='saved_recipes'),
    path('profile/', views.profile_view, name='profile'),
    path('toggle-favorite/<int:recipe_pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('new-recipe/', views.new_recipe, name='new_recipe'),
    path('recipe/<int:recipe_pk>/edit/', views.edit_recipe, name='edit_recipe'),
    path('scrape-recipe/', views.scrape_recipe, name='scrape_recipe'),
    path('generate-recipes/', views.generate_recipe, name="generate_recipes"),
    path('recipe/<int:recipe_pk>/translate/', views.translate_recipe_view, name="translate_recipe"),
    path('recipe/<int:recipe_pk>/audio/', views.generate_audio_for_recipe, name="audio_recipe"),
    path('recipe/<int:recipe_pk>/delete', views.delete_recipe, name="delete_recipe"),
    path('settings/', views.settings_view, name='settings'),
    path('settings/change-password/', views.change_password, name='change_password'),
    path('settings/delete-account/', views.delete_account, name='delete_account'),
    path('settings/change-translation-language/', views.change_translation_language, name="change_translation_language"),
    path("recipe/<int:recipe_pk>/print/", views.print_recipe, name="print_recipe")
]
