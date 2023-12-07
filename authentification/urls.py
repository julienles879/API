from django.urls import path

from .views import *


# Routage de l'application d'authentification
urlpatterns = [
    path('creation', UtilisateurCreationView.as_view(), name='creation-utilisateur'),
    path('connexion', UtilisateurConnexionView.as_view(), name='connexion-utilisateur'),
]
