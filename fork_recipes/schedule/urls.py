from django.urls import path
from . import views

app_name = 'schedule'



urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('create/', views.create_schedule_meal_type, name='create_schedule'),

]