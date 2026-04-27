from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('messages/', views.chatbot_messages, name='chatbot_messages'),
    path('messages/user/', views.chatbot_messages_user, name='chatbot_messages_user'),
    path('messages/studio/', views.chatbot_messages_studio, name='chatbot_messages_studio'),
    path('messages/admin/', views.chatbot_messages_admin, name='chatbot_messages_admin'),
    path('clear/', views.clear_chat_history, name='clear_chat_history'),
]
