from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('add-note/<int:booking_id>/', views.add_note, name='add_note'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Studio owner views
    path('approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
]
