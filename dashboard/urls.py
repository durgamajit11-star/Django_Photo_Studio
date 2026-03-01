from django.urls import path
from . import views

urlpatterns = [
    # USER
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('recommendations/', views.user_recommendations, name='user_recommendations'),
    path('explore/', views.explore_studios, name='explore_studios'),
    path('reviews/', views.user_reviews, name='user_reviews'),
    path('payments/', views.user_payments, name='user_payments'),
    path('notifications/', views.user_notifications, name='user_notifications'),

    # STUDIO
    path('studio/', views.studio_dashboard, name='studio_dashboard'),

    # ADMIN
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]