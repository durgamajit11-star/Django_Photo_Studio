from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from studios.models import Studio, Review
from accounts.decorators import role_required


@login_required
@role_required(['USER'])
def user_reviews(request):
    """Display all reviews by the current user"""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    context = {'reviews': reviews}
    return render(request, 'user/dashboard/user_reviews.html', context)


@login_required
@role_required(['STUDIO'])
def studio_reviews(request):
    """Display all reviews for the current studio"""
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')
    
    reviews = Review.objects.filter(studio=studio).order_by('-created_at')
    avg_rating = studio.average_rating() if hasattr(studio, 'average_rating') else 0
    
    context = {
        'studio': studio,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': reviews.count(),
        'high_ratings': reviews.filter(rating__gte=4).count(),
        'low_ratings': reviews.filter(rating__lt=3).count(),
    }
    return render(request, 'studio/dashboard/studio_reviews.html', context)


@login_required
@role_required(['USER'])
def add_review(request, studio_id):
    """Add or update a review for a studio"""
    studio = get_object_or_404(Studio, id=studio_id)
    
    # Check if user has already reviewed this studio
    existing_review = Review.objects.filter(studio=studio, user=request.user).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not all([rating, comment]):
            messages.error(request, 'Rating and comment are required')
            return redirect('studio_detail', studio_id=studio_id)
        
        try:
            if existing_review:
                # Update existing review
                existing_review.rating = int(rating)
                existing_review.comment = comment
                existing_review.save()
                messages.success(request, 'Review updated successfully!')
            else:
                # Create new review
                Review.objects.create(
                    studio=studio,
                    user=request.user,
                    rating=int(rating),
                    comment=comment
                )
                messages.success(request, 'Review posted successfully!')
            return redirect('studio_detail', studio_id=studio_id)
        except Exception as e:
            messages.error(request, f'Error posting review: {str(e)}')
            return redirect('studio_detail', studio_id=studio_id)
    
    context = {
        'studio': studio,
        'existing_review': existing_review,
    }
    return render(request, 'studios/add_review.html', context)


@login_required
@role_required(['USER'])
def delete_review(request, review_id):
    """Delete a review posted by the user"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    studio_id = review.studio.id
    review.delete()
    messages.success(request, 'Review deleted successfully!')
    return redirect('studio_detail', studio_id=studio_id)
