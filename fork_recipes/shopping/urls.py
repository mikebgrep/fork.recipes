from django.urls import path
from . import views

app_name = 'shopping'


urlpatterns = [
    path('', views.shopping_list, name="shopping_list"),
    path('delete/<int:list_pk>/', views.delete_list, name="delete_list"),
    path('create/', views.create_list, name="create_list"),
    path('<int:list_pk>/', views.get_shopping_list, name="single_shopping_list"),
    path('item/<int:item_pk>/', views.update_shopping_item, name="update_item"),
    path('<int:list_pk>/add-ingredient', views.add_shopping_list_item, name="add_item"),
    path('<int:list_pk>/delete/<int:item_pk>/', views.delete_shopping_list_item, name="remove_item"),
    path('complete/<int:item_pk>/', views.complete_single_shopping_list_item, name="complete_item"),
    path('<int:list_pk>/complete/', views.complete_shopping_list, name="complete_list"),
    path('add/<int:recipe_pk>/', views.add_shopping_list_recipe_items, name="add_recipe_to_list")
]