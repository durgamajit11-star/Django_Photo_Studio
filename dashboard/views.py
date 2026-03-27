from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.forms import UserUpdateForm
from django.contrib import messages
from django.db.models import Avg, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime

from accounts.models import CustomUser
from studios.models import Studio, Portfolio, Review
from django.db.models import Q 


def landing_page(request):
    return render(request, "landing.html")


def landing_explore_studio(request):
    return render(request, "landing_explore_studio.html")


def studio_payment(request):
    return render(request, "user/dashboard/studio_payment.html")

def studio_booking(request):
    return render(request, "user/dashboard/studio_booking.html")

@login_required
@role_required(['USER'])
def user_dashboard(request):
    return render(request, 'user/dashboard/user_dashboard.html')

@login_required
@role_required(['USER'])
def user_profile(request):

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'user/dashboard/user_profile.html', {'form': form})


@login_required
@role_required(['USER'])
def user_bookings(request):
    from bookings.models import BookingRequest
    bookings = BookingRequest.objects.filter(user=request.user).order_by('-created_at')
    context = {'bookings': bookings}
    return render(request, 'user/dashboard/user_bookings.html', context)

@login_required
@role_required(['USER'])
@login_required
@role_required(['USER'])
def user_recommendations(request):
    from recommendations.models import StudioRecommendation
    recommendations = StudioRecommendation.objects.filter(user=request.user).order_by('-score')[:12]
    return render(request, 'user/dashboard/user_recommendations.html', {'recommendations': recommendations})


@login_required
@role_required(['USER'])
def explore_studios(request):
    query = request.GET.get('q')
    location = request.GET.get('location')
    category = request.GET.get('category')
    sort = request.GET.get('sort')

    studios = Studio.objects.all()

   # 🔍 SMART SEARCH (FIX)
    if query:
        studios = studios.filter(
            Q(studio_name__icontains=query) |
            Q(description__icontains=query) |
            Q(specializations__icontains=query)
        )

    # 📍 Location filter
    if location:
        studios = studios.filter(location__icontains=location)

    # 🎯 Filter by category
    if category:
        studios = studios.filter(category__id=category)

    # 🔥 Sorting options
    if sort == 'rating':
        studios = sorted(studios, key=lambda s: s.average_rating(), reverse=True)
    elif sort == 'experience':
        studios = studios.order_by('-experience_years')
    elif sort == 'new':
        studios = studios.order_by('-created_at')

    # 🌟 Featured Studios
    featured_studios = Studio.objects.filter(is_featured=True)

    # 📂 Categories (for filter buttons)
    from studios.models import Category
    categories = Category.objects.all()

    context = {
        'studios': studios,
        'featured_studios': featured_studios,
        'categories': categories,
        'selected_category': category,
        'selected_sort': sort,
    }

    return render(request, 'user/dashboard/explore_studios.html', context)


@login_required
@role_required(['USER'])
def user_reviews(request):
    from studios.models import Review
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    context = {'reviews': reviews}
    return render(request, 'user/dashboard/user_reviews.html', context)


@login_required
@role_required(['USER'])
def user_payments(request):
    from payments.models import Payment
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    total_amount = sum(p.amount for p in payments if p.status == "Completed")
    context = {'payments': payments, 'total_amount': total_amount }
    return render(request, 'user/dashboard/user_payments.html', context)


@login_required
@role_required(['USER'])
def user_notifications(request):
    return render(request, 'user/dashboard/user_notifications.html')


@login_required
@role_required(['STUDIO'])
def studio_dashboard(request):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        # Create studio profile if doesn't exist
        try:
            studio = Studio.objects.create(
                user=request.user,
                studio_name=request.user.studio_name or f"{request.user.username}'s Studio",
                location=request.user.address or 'Not specified'
            )
            messages.success(request, 'Studio profile created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating studio profile: {str(e)}')
            return redirect('user_dashboard')
    
    # Get stats
    from bookings.models import BookingRequest
    total_bookings = studio.total_bookings()
    confirmed_bookings = studio.confirmed_bookings()
    avg_rating = studio.average_rating()
    total_earnings = BookingRequest.objects.filter(studio=studio, status='Confirmed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'studio': studio,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'avg_rating': avg_rating,
        'total_earnings': total_earnings,
    }
    return render(request, 'studio/dashboard/studio_dashboard.html', context)


@login_required
@role_required(['STUDIO'])
@login_required
@role_required(['STUDIO'])
def studio_portfolio(request):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')

    if request.method == 'POST':
        image = request.FILES.get('image')
        description = request.POST.get('description')
        
        if image and description:
            Portfolio.objects.create(
                studio=studio,
                image=image,
                description=description
            )
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('studio_portfolio')
        else:
            messages.error(request, 'Please provide both image and description')

    portfolios = Portfolio.objects.filter(studio=studio).order_by('-uploaded_at')

    return render(request, 'studio/dashboard/studio_portfolio.html', {
        'studio': studio,
        'portfolios': portfolios,
        'total_photos': portfolios.count()
    })


@login_required
@role_required(['STUDIO'])
def studio_bookings(request):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')
    
    from bookings.models import BookingRequest
    bookings = BookingRequest.objects.filter(studio=studio).order_by('-created_at')
    
    # Summary stats
    pending = bookings.filter(status='Pending').count()
    confirmed = bookings.filter(status='Confirmed').count()

    return render(request, 'studio/dashboard/studio_bookings.html', {
        'studio': studio,
        'bookings': bookings,
        'pending': pending,
        'confirmed': confirmed,
    })


@login_required
@role_required(['STUDIO'])
def studio_earnings(request):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')

    from bookings.models import BookingRequest
    from payments.models import Payment
    
    bookings = BookingRequest.objects.filter(studio=studio)
    total_earnings = bookings.filter(payment_status="Paid").aggregate(Sum('amount'))['amount__sum'] or 0
    total_bookings = bookings.count()
    completed_bookings = bookings.filter(status="Completed").count()
    pending_amount = bookings.filter(payment_status="Pending").aggregate(Sum('amount'))['amount__sum'] or 0
    recent_payments = Payment.objects.filter(booking_request__studio=studio).order_by('-created_at')[:10]

    return render(request, 'studio/dashboard/studio_earnings.html', {
        'total_earnings': total_earnings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_amount': pending_amount,
        'recent_payments': recent_payments,
    })


@login_required
@role_required(['STUDIO'])
def studio_reviews(request):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')

    from studios.models import Review
    reviews = Review.objects.filter(studio=studio).order_by('-created_at')
    avg_rating = studio.average_rating()

    return render(request, 'studio/dashboard/studio_reviews.html', {
        'studio': studio,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': reviews.count()
    })



@login_required
@role_required(['STUDIO'])
def delete_photo(request, photo_id):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')

    photo = get_object_or_404(Portfolio, id=photo_id, studio=studio)
    photo.delete()
    messages.success(request, 'Photo deleted successfully!')

    return redirect('studio_portfolio')


@login_required
@role_required(['STUDIO'])
def approve_booking(request, booking_id):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')

    from bookings.models import BookingRequest
    booking = get_object_or_404(BookingRequest, id=booking_id, studio=studio)
    booking.status = "Confirmed"
    booking.save()
    messages.success(request, 'Booking approved!')

    return redirect('studio_bookings')


@login_required
@role_required(['STUDIO'])
def cancel_booking(request, booking_id):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')

    from bookings.models import BookingRequest
    booking = get_object_or_404(BookingRequest, id=booking_id, studio=studio)
    booking.status = "Cancelled"
    booking.save()
    messages.success(request, 'Booking cancelled!')

    return redirect('studio_bookings')

@login_required
@role_required(['ADMIN'])
def admin_dashboard(request):

    total_users = CustomUser.objects.count()
    total_studios = Studio.objects.count()
    
    from bookings.models import BookingRequest
    total_bookings = BookingRequest.objects.count()

    total_revenue = BookingRequest.objects.filter(
        status="Confirmed"
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'total_users': total_users,
        'total_studios': total_studios,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
    }

    return render(request, "admin/dashboard/admin_dashboard.html", context)


from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
@role_required(['ADMIN'])
def manage_users(request):
    users = User.objects.filter(role='USER')   # ✅ only users
    return render(request, "admin/dashboard/manage_users.html", {"users": users})


from studios.models import Studio

@login_required
@role_required(['ADMIN'])
def manage_studios(request):
    studios = Studio.objects.select_related('user')   # ✅ correct
    return render(request, "admin/dashboard/manage_studios.html", {"studios": studios})


def approve_studio(request, id):
    studio = Studio.objects.get(id=id)
    studio.is_active = True
    studio.save()
    return redirect('manage_studios')


def reject_studio(request, id):
    studio = Studio.objects.get(id=id)
    studio.delete()
    return redirect('manage_studios')



@login_required
@role_required(['ADMIN'])
def admin_bookings(request):
    from bookings.models import BookingRequest
    
    bookings = BookingRequest.objects.select_related('user', 'studio').all()

    confirmed_count = bookings.filter(status="Confirmed").count()
    pending_count = bookings.filter(status="Pending").count()
    cancelled_count = bookings.filter(status="Cancelled").count()

    # ===== Monthly Revenue Data =====
    monthly_revenue = (
        BookingRequest.objects
        .filter(status="Confirmed")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    labels = []
    revenue_data = []

    for item in monthly_revenue:
        labels.append(item["month"].strftime("%b %Y"))
        revenue_data.append(float(item["total"]))

    context = {
        'bookings': bookings,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
        'revenue_labels': labels,
        'revenue_data': revenue_data,
    }

    return render(request, "admin/dashboard/admin_bookings.html", context)

@login_required
@role_required(['ADMIN'])
def admin_payments(request):
    return render(request, "admin/dashboard/admin_payments.html")