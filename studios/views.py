from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from studios.models import Studio, Portfolio, Review
from bookings.models import BookingRequest


# ==================== FEATURED/HOME VIEWS ====================

def featured_studios(request):
    """Display featured studios on homepage"""
    featured = Studio.objects.filter(is_featured=True).annotate(avg_rating=Avg('reviews__rating'))[:6]
    context = {'featured_studios': featured}
    return render(request, 'studios/featured_studios.html', context)


# ==================== PUBLIC VIEWS ====================

def studio_list(request):
    """Display all studios with search and filter functionality"""
    studios = Studio.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        studios = studios.filter(
            Q(studio_name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(specializations__icontains=search_query)
        )
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        studios = studios.filter(location__icontains=location)
    
    # Filter by verified only
    verified_only = request.GET.get('verified', False)
    if verified_only:
        studios = studios.filter(is_verified=True)
    
    # Filter by experience level
    min_experience = request.GET.get('experience', '')
    if min_experience:
        try:
            studios = studios.filter(experience_years__gte=int(min_experience))
        except ValueError:
            pass
    
    # Sort options
    sort = request.GET.get('sort', '-created_at')
    if sort in ['studio_name', '-studio_name', 'created_at', '-created_at', 'experience_years']:
        studios = studios.order_by(sort)
    
    # Annotate with average rating
    studios = studios.annotate(avg_rating=Avg('reviews__rating'))
    
    # Pagination
    paginator = Paginator(studios, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'studios': page_obj.object_list,
        'search_query': search_query,
        'location': location,
        'verified_only': verified_only,
        'min_experience': min_experience,
        'sort': sort,
        'total_studios': paginator.count,
    }
    
    return render(request, 'studios/studio_list.html', context)


def studio_detail(request, studio_id):
    """Display detailed information about a specific studio"""
    studio = get_object_or_404(Studio, id=studio_id)
    portfolios = studio.portfolios.all()
    reviews = studio.reviews.all()
    
    context = {
        'studio': studio,
        'portfolios': portfolios,
        'reviews': reviews,
        'avg_rating': studio.average_rating(),
        'total_reviews': reviews.count(),
        'total_bookings': studio.total_bookings(),
    }
    
    return render(request, 'studios/studio_detail.html', context)


def studio_portfolio(request, studio_id):
    """Display portfolio for a specific studio"""
    studio = get_object_or_404(Studio, id=studio_id)
    portfolios = studio.portfolios.all()
    
    # Pagination for portfolio
    paginator = Paginator(portfolios, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'studio': studio,
        'page_obj': page_obj,
        'portfolios': page_obj.object_list,
    }
    
    return render(request, 'studios/studio_portfolio.html', context)


def studio_reviews(request, studio_id):
    """Display reviews for a specific studio"""
    studio = get_object_or_404(Studio, id=studio_id)
    reviews = studio.reviews.all()
    
    # Pagination for reviews
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'studio': studio,
        'page_obj': page_obj,
        'reviews': page_obj.object_list,
        'avg_rating': studio.average_rating(),
    }
    
    return render(request, 'studios/studio_reviews.html', context)


# ==================== USER AUTHENTICATED VIEWS ====================

@login_required
def user_studios_list(request):
    """Users can browse and filter studios"""
    return studio_list(request)


@login_required
def book_studio(request, studio_id):
    """Create a booking with a studio"""
    studio = get_object_or_404(Studio, id=studio_id)
    
    if request.method == 'POST':
        event_type = request.POST.get('event_type')
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        
        if not all([event_type, date, amount]):
            messages.error(request, 'All fields are required')
            return redirect('studio_detail', studio_id=studio_id)
        
        try:
            booking = BookingRequest.objects.create(
                studio=studio,
                user=request.user,
                event_type=event_type,
                date=date,
                amount=amount
            )
            messages.success(request, 'Booking created successfully!')
            return redirect('user_bookings')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('studio_detail', studio_id=studio_id)
    
    context = {'studio': studio}
    return render(request, 'studios/book_studio.html', context)


@login_required
def add_review(request, studio_id):
    """Add a review for a studio"""
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
                existing_review.rating = rating
                existing_review.comment = comment
                existing_review.save()
                messages.success(request, 'Review updated successfully!')
            else:
                # Create new review
                Review.objects.create(
                    studio=studio,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, 'Review added successfully!')
            return redirect('studio_detail', studio_id=studio_id)
        except Exception as e:
            messages.error(request, f'Error saving review: {str(e)}')
            return redirect('studio_detail', studio_id=studio_id)
    
    context = {
        'studio': studio,
        'existing_review': existing_review,
    }
    return render(request, 'studios/add_review.html', context)
