from django.urls import path
from . import views

urlpatterns = [
    path("conversations/", views.conversations, name='conversations'),
    path("messages/", views.messages, name='messages'),
]