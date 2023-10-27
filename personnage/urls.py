from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('creation', PersonnageCreationView.as_view(), name='creation-personnage'),
    path('univers/<int:univers_id>/liste', PersonnageListeView.as_view(), name='liste-personnage'),
    path('univers/<int:univers_id>/personnage/<int:personnage_id>/modifier/', PersonnageModifView.as_view(), name='modifier-personnage'),
    path('univers/<int:univers_id>/personnage/<int:personnage_id>/supprimer/', PersonnageSuppView.as_view(), name='supprimer-personnage'),
]