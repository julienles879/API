from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('creation', UniversCreationView.as_view(), name='creation-univers'),
    path('liste', UniversListeView.as_view(), name='liste-univers'),
    path('<int:univers_id>', UniversDetailView.as_view(), name='detail-univers'),
    path('modifier/<int:univers_id>', UniversModifView.as_view(), name='modifier-univers'),
    path('supprimer/<int:univers_id>', UniversSuppView.as_view(), name='supprimer-univers'),
]