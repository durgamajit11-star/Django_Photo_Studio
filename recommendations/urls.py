from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.user_recommendations, name='recommendations_list'),
    path('refresh/', views.refresh_recommendations, name='refresh_recommendations'),
]
