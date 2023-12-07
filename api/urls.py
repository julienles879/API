from django.contrib import admin
from django.urls import path, include


# Routage du Projet
urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
    path('utilisateur/', include('utilisateur.urls')),
    path('univers/', include('univers.urls')),
    path('personnage/', include('personnage.urls')),
    path('conversation/', include('conversation.urls')),
    path('message/', include('message.urls')),
]
