from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.forms import UserUpdateForm
from django.contrib import messages
from django.db.models import Avg, Avg, Sum

from accounts.models import CustomUser
from .models import Review, Review, Studio, Booking, Portfolio
from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from django.db.models.functions import TruncMonth



def landing_page(request):
    return render(request, "landing.html")

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
    return render(request, 'user/dashboard/user_bookings.html')

@login_required
@role_required(['USER'])
def user_recommendations(request):
    return render(request, 'user/dashboard/user_recommendations.html')


@login_required
@role_required(['USER'])
def explore_studios(request):
    return render(request, 'user/dashboard/explore_studios.html')


@login_required
@role_required(['USER'])
def user_reviews(request):
    return render(request, 'user/dashboard/user_reviews.html')


@login_required
@role_required(['USER'])
def user_payments(request):
    return render(request, 'user/dashboard/user_payments.html')


@login_required
@role_required(['USER'])
def user_notifications(request):
    return render(request, 'user/dashboard/user_notifications.html')


@login_required
@role_required(['STUDIO'])
def studio_dashboard(request):
    return render(request, 'studio/dashboard/studio_dashboard.html')


@login_required
@role_required(['STUDIO'])
def studio_portfolio(request):
    studio = Studio.objects.filter(user=request.user).first()

    photos = Portfolio.objects.filter(studio=studio)

    return render(request, 'studio/dashboard/studio_portfolio.html', {
        'photos': photos
    })


@login_required
@role_required(['STUDIO'])
def studio_bookings(request):
    studio = Studio.objects.filter(user=request.user).first()

    bookings = Booking.objects.filter(studio=studio).order_by('-created_at')

    return render(request, 'studio/dashboard/studio_bookings.html', {
        'bookings': bookings
    })


@login_required
@role_required(['STUDIO'])
def studio_earnings(request):
    studio = Studio.objects.filter(user=request.user).first()

    from django.db.models import Sum
    total_earnings = Booking.objects.filter(
        studio=studio,
        payment_status="Paid"
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'studio/dashboard/studio_earnings.html', {
        'total_earnings': total_earnings
    })


@login_required
@role_required(['STUDIO'])
def studio_reviews(request):
    studio = Studio.objects.filter(user=request.user).first()

    reviews = Review.objects.filter(studio=studio).order_by('-created_at')

    return render(request, 'studio/dashboard/studio_reviews.html', {
        'reviews': reviews
    })



@login_required
@role_required(['STUDIO'])
def delete_photo(request, photo_id):
    studio = Studio.objects.filter(user=request.user).first()

    photo = get_object_or_404(Portfolio, id=photo_id, studio=studio)
    photo.delete()

    return redirect('studio/dashboard/ studio_portfolio.html')


@login_required
@role_required(['STUDIO'])
def approve_booking(request, booking_id):
    studio = Studio.objects.filter(user=request.user).first()

    booking = get_object_or_404(Booking, id=booking_id, studio=studio)
    booking.status = "Confirmed"
    booking.save()

    return redirect('studio_bookings')


@login_required
@role_required(['STUDIO'])
def cancel_booking(request, booking_id):
    studio = Studio.objects.filter(user=request.user).first()

    booking = get_object_or_404(Booking, id=booking_id, studio=studio)
    booking.status = "Cancelled"
    booking.save()

    return redirect('studio_bookings')

@login_required
@role_required(['ADMIN'])
def admin_dashboard(request):

    total_users = CustomUser.objects.count()
    total_studios = Studio.objects.count()
    total_bookings = Booking.objects.count()

    total_revenue = Booking.objects.filter(
        status="Confirmed"
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'total_users': total_users,
        'total_studios': total_studios,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
    }

    return render(request, "admin/dashboard/admin_dashboard.html", context)


@login_required
@role_required(['ADMIN'])
def manage_users(request):
    return render(request, "admin/dashboard/manage_users.html")


@login_required
@role_required(['ADMIN'])
def manage_studios(request):
    return render(request, "admin/dashboard/manage_studios.html")


@login_required
@role_required(['ADMIN'])
def admin_bookings(request):

    bookings = Booking.objects.select_related('user', 'studio').all()

    confirmed_count = bookings.filter(status="Confirmed").count()
    pending_count = bookings.filter(status="Pending").count()
    cancelled_count = bookings.filter(status="Cancelled").count()

    # ===== Monthly Revenue Data =====
    monthly_revenue = (
        Booking.objects
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