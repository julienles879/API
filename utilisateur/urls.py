from django.contrib import admin
from django.urls import path

from .views import *


# Routage de l'application utilisateur.
urlpatterns = [
    path('liste', UtilisateurListeView.as_view(), name='liste-utilisateur'),
    path('<int:utilisateur_id>', UtilisateurDetailView.as_view(), name='detail-utilisateur'),
    path('modification/<int:utilisateur_id>', UtilisateurModificationView.as_view(), name="modification-utilisateur")
]