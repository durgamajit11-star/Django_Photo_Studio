from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudioRecommendation
from studios.models import Studio
from accounts.decorators import role_required


@login_required
@role_required(['USER'])
def user_recommendations(request):
    """Display AI-powered studio recommendations for the current user"""
    try:
        # Get recommendations for user, sorted by score (highest first)
        recommendations = StudioRecommendation.objects.filter(
            user=request.user
        ).select_related('studio').order_by('-score')[:12]
        
        # Ensure scores are between 0-100
        for rec in recommendations:
            if hasattr(rec, 'score'):
                rec.score = max(0, min(100, int(rec.score)))
    except Exception as e:
        messages.warning(request, f'Error loading recommendations: {str(e)}')
        recommendations = []
    
    context = {
        'recommendations': recommendations,
        'total_recommendations': len(recommendations),
    }
    return render(request, 'user/dashboard/user_recommendations.html', context)


@login_required
@role_required(['USER'])
def refresh_recommendations(request):
    """Refresh recommendations for the current user"""
    try:
        # Delete old recommendations
        StudioRecommendation.objects.filter(user=request.user).delete()
        
        # TODO: Implement AI recommendation algorithm here
        # For now, get random featured/high-rated studios
        studios = Studio.objects.filter(
            is_featured=True
        ).order_by('-created_at')[:5]
        
        # Create new recommendations
        for i, studio in enumerate(studios):
            score = 100 - (i * 10)  # Decreasing score
            StudioRecommendation.objects.create(
                user=request.user,
                studio=studio,
                score=score
            )
        
        messages.success(request, 'Recommendations refreshed!')
    except Exception as e:
        messages.error(request, f'Error refreshing recommendations: {str(e)}')
    
    return redirect('user_recommendations')