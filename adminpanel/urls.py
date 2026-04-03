from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/toggle-status/<int:id>/', views.toggle_user_status, name='toggle_user_status'),
    path('users/delete/<int:id>/', views.delete_user, name='delete_user'),
    path('studios/', views.manage_studios, name='manage_studios'),
    path('studios/approve/<int:id>/', views.approve_studio, name='approve_studio'),
    path('studios/reject/<int:id>/', views.reject_studio, name='reject_studio'),
    path('bookings/', views.admin_bookings, name='admin_bookings'),
    path('bookings/cancel/<int:id>/', views.admin_cancel_booking, name='admin_cancel_booking'),
    path('payments/', views.admin_payments, name='admin_payments'),
]
