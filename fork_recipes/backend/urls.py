from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns = [
        path('', include('recipes.urls', namespace="recipes")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = [
        path('', include('recipes.urls', namespace="recipes")),
    ]