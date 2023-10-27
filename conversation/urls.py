from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('creation/', ConversationCreationView.as_view(), name='creation-conversation'),
    path('liste/', ConversationListeView.as_view(), name='liste-conversation'),
    path('detail/<int:conversation_id>/', ConversationDetailView.as_view(), name='detail-conversation'),
    path('<int:conversation_id>/supprimer/', ConversationSuppView.as_view(), name='supprimer-conversation'),
]