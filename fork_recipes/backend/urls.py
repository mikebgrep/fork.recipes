from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from recipes import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if settings.DEBUG:
    urlpatterns = [
        path('', include('recipes.urls', namespace="recipes")),
        path('schedule/', include('schedule.urls', namespace="schedule")),
        path('shopping/', include('shopping.urls', namespace="shopping")),
        path('settings/', include('settings.urls', namespace="settings")),

                  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + staticfiles_urlpatterns()
else:
    urlpatterns = [
        path('', include('recipes.urls', namespace="recipes")),
        path('schedule/', include('schedule.urls', namespace="schedule")),
        path('shopping/', include('shopping.urls', namespace="shopping")),
        path('settings/', include('settings.urls', namespace="settings")),
    ]


handler404 = views.handler404
handler500 = views.handler500