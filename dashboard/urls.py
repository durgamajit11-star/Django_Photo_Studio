from django.urls import path, include
from . import views

urlpatterns = [
    # USER
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('payment/', views.studio_payment, name='studio_payment'),
    path('user/booking/', views.studio_booking, name='studio_booking'),
    path('profile/', views.user_profile, name='user_profile'),
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('recommendations/', views.user_recommendations, name='user_recommendations'),
    path('explore/', views.explore_studios, name='explore_studios'),
    path('reviews/', views.user_reviews, name='user_reviews'),
    path('payments/', views.user_payments, name='user_payments'),
    path('notifications/', views.user_notifications, name='user_notifications'),

    #=============== STUDIO===============#
    
    # ================= STUDIO DASHBOARD =================
    path('studio/', views.studio_dashboard, name='studio_dashboard'),

    # ================= PORTFOLIO =================
    path('studio/portfolio/', views.studio_portfolio, name='studio_portfolio'),
    path('studio/portfolio/delete/<int:photo_id>/', views.delete_photo, name='delete_photo'),

    # ================= BOOKINGS =================
    path('studio/bookings/', views.studio_bookings, name='studio_bookings'),
    path('studio/bookings/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('studio/bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # ================= EARNINGS =================
    path('studio/earnings/', views.studio_earnings, name='studio_earnings'),

    # ================= REVIEWS =================
    path('studio/reviews/', views.studio_reviews, name='studio_reviews'),

    # ================= PROFILE =================
    path('studio/profile/', views.studio_profile, name='studio_profile'),
    path('studio/profile/preferences/', views.save_studio_preferences, name='save_studio_preferences'),
    path('studio/profile/logout-all/', views.logout_all_devices, name='logout_all_devices'),
    path('studio/profile/delete-account/', views.delete_studio_account, name='delete_studio_account'),

    # ADMIN APP ROUTES
    path('admin/', include('adminpanel.urls')),
]