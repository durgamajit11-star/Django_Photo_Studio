from django.urls import path
from . import views

app_name = 'studios'

urlpatterns = [
    # ==================== PUBLIC STUDIO VIEWS ====================
    path('', views.studio_list, name='studio_list'),
    path('featured/', views.featured_studios, name='featured_studios'),
    path('studio/<int:studio_id>/', views.studio_detail, name='studio_detail'),
    path('portfolio/<int:studio_id>/', views.studio_portfolio, name='studio_portfolio'),
    path('reviews/<int:studio_id>/', views.studio_reviews, name='studio_reviews'),
    
    # ==================== USER AUTHENTICATED VIEWS ====================
    path('browse/', views.user_studios_list, name='user_studios_list'),
    path('book/<int:studio_id>/', views.book_studio, name='book_studio'),
    path('review/<int:studio_id>/', views.add_review, name='add_review'),
]
