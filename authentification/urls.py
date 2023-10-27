from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('creation', UtilisateurCreationView.as_view(), name='creation-utilisateur'),
    path('connexion', UtilisateurConnexionView.as_view(), name='connexion-utilisateur'),
]
