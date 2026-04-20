from django.urls import path
from . import views

app_name = 'studios'

urlpatterns = [
    # ==================== PUBLIC STUDIO VIEWS ====================
    path('studio/<int:studio_id>/', views.studio_detail, name='studio_detail'),
    
    # ==================== USER AUTHENTICATED VIEWS ====================
    path('browse/', views.user_studios_list, name='user_studios_list'),
    path('book/<int:studio_id>/', views.book_studio, name='book_studio'),
    path('review/<int:studio_id>/', views.add_review, name='add_review'),
]
