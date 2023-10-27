from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('conversation/<int:id_conversation>/creation/', MessageCreationView.as_view(), name='creation-message'),
    path('conversation/<int:id_conversation>/historique/', MessageHistoriqueView.as_view(), name='historique-message'),
    path('conversation/<int:id_conversation>/dernier/', MessageDernierView.as_view(), name='dernier-message'),
]