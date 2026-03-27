from django.urls import path
from . import views

urlpatterns = [
    path('notifications', views.user_notifications, name='notifications'),
    path('read/<int:id>/', views.mark_as_read, name='mark_read'),
]