from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('messages/', views.chatbot_messages, name='chatbot_messages'),
    path('clear/', views.clear_chat_history, name='clear_chat_history'),
]
