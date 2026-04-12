from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from studios.models import Studio, Portfolio, Review, Service, StudioImage
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
    portfolios = studio.portfolios.all()[:12]
    studio_images = studio.studio_images.all()[:12]
    services = studio.services.all().order_by('price', 'service_name')
    reviews = studio.reviews.select_related('user').all()

    related_studios = Studio.objects.filter(
        Q(category=studio.category) | Q(location__icontains=studio.location),
    ).exclude(id=studio.id).order_by('-is_featured', '-created_at').distinct()[:4]

    recent_reviews = reviews[:6]
    specialization_tags = [item.strip() for item in (studio.specializations or '').split(',') if item.strip()]

    min_service_price = services.order_by('price').values_list('price', flat=True).first()
    max_service_price = services.order_by('-price').values_list('price', flat=True).first()
    existing_user_review = None
    if request.user.is_authenticated:
        existing_user_review = reviews.filter(user=request.user).first()
    
    context = {
        'studio': studio,
        'portfolios': portfolios,
        'studio_images': studio_images,
        'services': services,
        'reviews': recent_reviews,
        'related_studios': related_studios,
        'specialization_tags': specialization_tags,
        'avg_rating': studio.average_rating(),
        'total_reviews': reviews.count(),
        'total_bookings': studio.total_bookings(),
        'confirmed_bookings': studio.confirmed_bookings(),
        'avg_booking_value': studio.average_booking_value(),
        'portfolio_count': portfolios.count(),
        'gallery_count': studio_images.count(),
        'service_count': services.count(),
        'min_service_price': min_service_price,
        'max_service_price': max_service_price,
        'existing_user_review': existing_user_review,
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
        service_id = request.POST.get('service_id')
        event_type = request.POST.get('event_type')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        amount = request.POST.get('amount')
        
        if not all([event_type, date]):
            messages.error(request, 'Event type and date are required')
            return redirect('studio_detail', studio_id=studio_id)
        
        try:
            service = None
            if service_id:
                service = Service.objects.filter(id=service_id, studio=studio).first()

            total_price = amount
            if service and service.price is not None:
                total_price = service.price

            if not total_price:
                total_price = studio.price_per_hour or 0

            booking = BookingRequest.objects.create(
                studio=studio,
                user=request.user,
                service=service,
                event_type=event_type,
                date=date,
                booking_date=date,
                time_slot=time_slot,
                amount=total_price,
                total_price=total_price
            )
            messages.success(request, 'Booking created successfully!')
            return redirect('user_bookings')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('studio_detail', studio_id=studio_id)
    
    context = {
        'studio': studio,
        'services': Service.objects.filter(studio=studio).order_by('service_name')
    }
    return render(request, 'studios/book_studio.html', context)


@login_required
def add_review(request, studio_id):
    """Add or update a review for a studio"""
    from bookings.models import BookingRequest

    studio = get_object_or_404(Studio, id=studio_id)
    
    # Check if user has already reviewed this studio
    existing_review = Review.objects.filter(studio=studio, user=request.user).first()
    has_eligible_booking = BookingRequest.objects.filter(
        user=request.user,
        studio=studio,
        status__in=['Confirmed', 'Completed']
    ).exists()

    if not has_eligible_booking:
        messages.error(request, 'You can review this studio only after a confirmed booking.')
        return redirect('studios:studio_detail', studio_id=studio.id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not all([rating, comment]):
            messages.error(request, 'Rating and comment are required')
            return redirect('studios:add_review', studio_id=studio_id)
        
        try:
            rating_value = int(rating)
            if rating_value < 1 or rating_value > 5:
                raise ValueError('Rating out of range')

            if existing_review:
                # Update existing review
                existing_review.rating = rating_value
                existing_review.comment = comment
                existing_review.save(update_fields=['rating', 'comment', 'updated_at'])
                messages.success(request, 'Review updated successfully!')
            else:
                # Create new review
                Review.objects.create(
                    studio=studio,
                    user=request.user,
                    rating=rating_value,
                    comment=comment
                )
                messages.success(request, 'Review added successfully!')
            return redirect('studios:studio_detail', studio_id=studio_id)
        except Exception as e:
            messages.error(request, f'Error saving review: {str(e)}')
            return redirect('studios:add_review', studio_id=studio_id)
    
    context = {
        'studio': studio,
        'existing_review': existing_review,
    }
    return render(request, 'studios/add_review.html', context)
