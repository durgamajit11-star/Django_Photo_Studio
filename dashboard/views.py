from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from accounts.decorators import role_required
from accounts.forms import UserUpdateForm
from django.contrib import messages
from django.db.models import Avg, Sum, Count, Min, Max
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
import json
import re

from studios.models import Studio, Portfolio, Review
from django.db.models import Q 
from .models import StudioPreference


def landing_page(request):
    return render(request, "landing.html")


def landing_explore_studio(request):
    return render(request, "landing_explore_studio.html")


@login_required
@role_required(['USER'])
def studio_payment(request):
    from bookings.models import BookingRequest
    from payments.models import Payment

    upi_id_pattern = re.compile(r'^[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}$')
    payee_upi_id = 'studiosync@upi'
    payee_name = 'StudioSync'

    unpaid_bookings = BookingRequest.objects.filter(
        user=request.user,
        payment_status='Unpaid'
    ).exclude(status='Cancelled').select_related('studio').order_by('date', 'time')

    selected_booking_id = request.POST.get('booking_id') or request.GET.get('booking_id')
    selected_booking = None
    if selected_booking_id:
        selected_booking = unpaid_bookings.filter(id=selected_booking_id).first()
    if not selected_booking:
        selected_booking = unpaid_bookings.first()

    if request.method == 'POST':
        if not selected_booking:
            messages.error(request, 'Please select a valid unpaid booking first')
            return redirect('studio_payment')

        payment_method = request.POST.get('payment_method', '').strip()
        payer_upi_id = request.POST.get('payer_upi_id', '').strip().lower()
        upi_reference = request.POST.get('upi_reference', '').strip().upper()
        valid_methods = {code for code, _ in Payment.PAYMENT_METHOD_CHOICES}

        if payment_method not in valid_methods:
            messages.error(request, 'Please select a valid payment method')
            return redirect(f"{request.path}?booking_id={selected_booking.id}")

        existing_payment = getattr(selected_booking, 'payment', None)
        if existing_payment:
            messages.warning(request, 'Payment already exists for this booking')
            return redirect('payments:payment_detail', payment_id=existing_payment.id)

        if payment_method == 'UPI':
            if payer_upi_id and not upi_id_pattern.match(payer_upi_id):
                messages.error(request, 'Please enter a valid UPI ID (example: name@bank)')
                return redirect(f"{request.path}?booking_id={selected_booking.id}")
            if not upi_reference or len(upi_reference) < 8:
                messages.error(request, 'Please enter a valid UPI reference/UTR (minimum 8 characters)')
                return redirect(f"{request.path}?booking_id={selected_booking.id}")

        try:
            payment = Payment.objects.create(
                booking=selected_booking,
                user=request.user,
                amount=selected_booking.amount,
                payment_method=payment_method,
                status='Processing'
            )

            if payment_method == 'UPI':
                payment.transaction_id = f"UPI-{upi_reference}-{payment.id:04d}"
            else:
                payment.transaction_id = f"TXN{payment.id:06d}"

            payment.status = 'Completed'
            payment.completed_at = timezone.now()
            payment.save()

            selected_booking.payment_status = 'Paid'
            selected_booking.save(update_fields=['payment_status', 'updated_at'])

            messages.success(request, 'Payment successful. Booking is now confirmed for payment.')
            return redirect('payments:payment_detail', payment_id=payment.id)
        except Exception as exc:
            messages.error(request, f'Unable to process payment: {exc}')
            return redirect(f"{request.path}?booking_id={selected_booking.id}")

    upi_payload = None
    if selected_booking:
        amount_str = f"{Decimal(selected_booking.amount):.2f}"
        note = f"Studio booking #{selected_booking.id}"
        upi_intent = (
            f"upi://pay?pa={quote(payee_upi_id)}"
            f"&pn={quote(payee_name)}"
            f"&am={amount_str}"
            f"&cu=INR"
            f"&tn={quote(note)}"
        )
        upi_payload = {
            'upi_id': payee_upi_id,
            'upi_name': payee_name,
            'upi_intent': upi_intent,
            'upi_qr_url': f"https://chart.googleapis.com/chart?cht=qr&chs=340x340&chl={quote(upi_intent, safe='')}",
        }

    context = {
        'unpaid_bookings': unpaid_bookings[:12],
        'selected_booking': selected_booking,
        'upi_payload': upi_payload,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, "user/dashboard/studio_payment.html", context)

@login_required
@role_required(['USER'])
def studio_booking(request):
    from bookings.models import BookingRequest
    from studios.models import Service

    camera_options = [
        {'code': 'none', 'label': 'Use Studio Default Camera Setup', 'price': Decimal('0')},
        {'code': 'dslr_basic', 'label': 'DSLR Basic Kit', 'price': Decimal('1200')},
        {'code': 'mirrorless_pro', 'label': 'Mirrorless Pro Kit', 'price': Decimal('2500')},
        {'code': 'cinema_4k', 'label': 'Cinema 4K Camera Kit', 'price': Decimal('4200')},
    ]
    camera_price_map = {opt['code']: opt['price'] for opt in camera_options}
    camera_label_map = {opt['code']: opt['label'] for opt in camera_options}
    gst_rate = Decimal('0.18')

    selected_studio_id = request.POST.get('studio_id') or request.GET.get('studio_id')
    if not str(selected_studio_id or '').isdigit():
        messages.info(request, 'Please select a studio from Explore or Studio Detail to start booking.')
        return redirect('explore_studios')

    selected_studio = Studio.objects.filter(id=selected_studio_id).first()
    if not selected_studio:
        messages.error(request, 'Selected studio was not found.')
        return redirect('explore_studios')

    services_queryset = Service.objects.filter(studio=selected_studio).order_by('service_name')

    if request.method == 'POST':
        event_type = request.POST.get('event_type', '').strip()
        booking_date = request.POST.get('date')
        time_slot = request.POST.get('time_slot', '').strip()
        location = request.POST.get('location', '').strip()
        special_requirements = request.POST.get('special_requirements', '').strip()
        service_id = request.POST.get('service_id')
        camera_option = request.POST.get('camera_option', 'none').strip()
        duration_raw = request.POST.get('duration_hours', '').strip()

        if not event_type or not booking_date:
            messages.error(request, 'Event type and booking date are required')
            return redirect(f"{request.path}?studio_id={selected_studio.id}")

        service = None
        if service_id:
            service = Service.objects.filter(id=service_id, studio=selected_studio).first()

        try:
            duration_hours = int(duration_raw or 2)
            if duration_hours <= 0 or duration_hours > 24:
                raise ValueError
        except ValueError:
            messages.error(request, 'Duration must be between 1 and 24 hours')
            return redirect(f"{request.path}?studio_id={selected_studio.id}")

        if camera_option not in camera_price_map:
            camera_option = 'none'

        base_rate = selected_studio.price_per_hour or Decimal('0')
        base_price = (base_rate * Decimal(duration_hours)).quantize(Decimal('0.01'))
        service_price = (service.price if service and service.price is not None else Decimal('0')).quantize(Decimal('0.01'))
        camera_price = camera_price_map[camera_option].quantize(Decimal('0.01'))

        subtotal = (base_price + service_price + camera_price).quantize(Decimal('0.01'))
        gst_amount = (subtotal * gst_rate).quantize(Decimal('0.01'))
        total_amount = (subtotal + gst_amount).quantize(Decimal('0.01'))

        if total_amount <= 0:
            messages.error(request, 'Unable to compute total bill. Please contact studio or choose another package.')
            return redirect(f"{request.path}?studio_id={selected_studio.id}")

        notes_lines = []
        if special_requirements:
            notes_lines.append(f"User Notes: {special_requirements}")
        if service:
            notes_lines.append(f"Service: {service.service_name} (Rs. {service_price})")
        if camera_option != 'none':
            notes_lines.append(f"Camera: {camera_label_map[camera_option]} (Rs. {camera_price})")
        notes_lines.append(f"Base Price: Rs. {base_price}")
        notes_lines.append(f"GST (18%): Rs. {gst_amount}")

        final_notes = "\n".join(notes_lines)

        booking = BookingRequest.objects.create(
            studio=selected_studio,
            user=request.user,
            service=service,
            event_type=event_type,
            date=booking_date,
            booking_date=booking_date,
            time_slot=time_slot,
            duration_hours=duration_hours,
            location=location or selected_studio.location,
            special_requirements=final_notes,
            amount=total_amount,
            total_price=total_amount,
        )

        messages.success(request, 'Booking created successfully. Complete payment to confirm.')
        return redirect(f"{reverse('studio_payment')}?booking_id={booking.id}")

    context = {
        'selected_studio': selected_studio,
        'services': services_queryset,
        'camera_options': camera_options,
        'gst_percent': int(gst_rate * 100),
        'recent_bookings': BookingRequest.objects.filter(user=request.user).select_related('studio').order_by('-created_at')[:6],
    }
    return render(request, "user/dashboard/studio_booking.html", context)

@login_required
@role_required(['USER'])
def user_dashboard(request):
    from bookings.models import BookingRequest
    from payments.models import Payment
    from recommendations.models import StudioRecommendation
    from studios.models import Review

    featured_studios = Studio.objects.order_by('-is_featured', '-is_verified', '-created_at')[:4]
    user_bookings = BookingRequest.objects.filter(user=request.user)
    recent_bookings = user_bookings.select_related('studio').order_by('-created_at')[:4]
    upcoming_booking = user_bookings.exclude(status='Cancelled').order_by('date', 'time').first()

    recent_payments = Payment.objects.filter(user=request.user).select_related('booking', 'booking__studio').order_by('-created_at')[:4]
    recent_reviews = Review.objects.filter(user=request.user).select_related('studio').order_by('-created_at')[:3]
    recommendations = StudioRecommendation.objects.filter(user=request.user).select_related('studio').order_by('-score')[:4]

    price_insights = Studio.objects.aggregate(
        min_price=Min('price_per_hour'),
        max_price=Max('price_per_hour'),
        avg_price=Avg('price_per_hour'),
    )

    trending_categories = (
        Studio.objects
        .exclude(category__isnull=True)
        .values('category__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    active_booking = user_bookings.exclude(status='Cancelled').order_by('-updated_at').first()
    booking_timeline = []
    if active_booking:
        booking_timeline = [
            {'label': 'Request Submitted', 'done': True},
            {'label': 'Studio Confirmed', 'done': active_booking.status in ['Confirmed', 'Completed']},
            {'label': 'Payment Completed', 'done': active_booking.payment_status == 'Paid'},
            {'label': 'Shoot Completed', 'done': active_booking.status == 'Completed'},
        ]

    recommendation_reasons = [
        {
            'studio': rec.studio,
            'score': rec.score,
            'reason': rec.reason or 'Matched based on your recent activity and preferences.',
        }
        for rec in recommendations
    ]

    trust_metrics = {
        'verified_studios': Studio.objects.filter(is_verified=True).count(),
        'secure_payments': 'UPI/Card/Wallet protected checkout',
        'support': '24x7 assistance via dashboard and chatbot',
        'refund_policy': 'Refund requests available from payment history',
    }

    spotlight_offers = [
        {'title': 'First Booking Offer', 'desc': 'Get priority support on your first confirmed booking.'},
        {'title': 'Bundle Value Pack', 'desc': 'Combine shoot + editing for better package value.'},
        {'title': 'Prime Time Slots', 'desc': 'Book early for weekend slots at top-rated studios.'},
    ]

    context = {
        'featured_studios': featured_studios,
        'total_bookings': user_bookings.count(),
        'pending_bookings': user_bookings.filter(status='Pending').count(),
        'confirmed_bookings': user_bookings.filter(status='Confirmed').count(),
        'completed_bookings': user_bookings.filter(status='Completed').count(),
        'upcoming_booking': upcoming_booking,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
        'recent_reviews': recent_reviews,
        'recommendations': recommendations,
        'recommendation_reasons': recommendation_reasons,
        'price_insights': price_insights,
        'trending_categories': trending_categories,
        'active_booking': active_booking,
        'booking_timeline': booking_timeline,
        'trust_metrics': trust_metrics,
        'spotlight_offers': spotlight_offers,
    }
    return render(request, 'user/dashboard/user_dashboard.html', context)

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
    status = request.GET.get('status', '').strip()
    search = request.GET.get('search', '').strip()

    base_queryset = BookingRequest.objects.filter(user=request.user)
    bookings = base_queryset.order_by('-created_at')

    if status:
        bookings = bookings.filter(status=status)

    if search:
        bookings = bookings.filter(
            Q(studio__studio_name__icontains=search)
            | Q(event_type__icontains=search)
            | Q(location__icontains=search)
        )

    context = {
        'bookings': bookings,
        'status': status,
        'search': search,
        'total_bookings': base_queryset.count(),
        'pending_count': base_queryset.filter(status='Pending').count(),
        'confirmed_count': base_queryset.filter(status='Confirmed').count(),
        'completed_count': base_queryset.filter(status='Completed').count(),
        'cancelled_count': base_queryset.filter(status='Cancelled').count(),
    }
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
    status = request.GET.get('status', '').strip()
    method = request.GET.get('method', '').strip()
    search = request.GET.get('search', '').strip()

    base_queryset = Payment.objects.filter(user=request.user)
    payments = base_queryset.order_by('-created_at')

    if status:
        payments = payments.filter(status=status)

    if method:
        payments = payments.filter(payment_method=method)

    if search:
        payments = payments.filter(
            Q(transaction_id__icontains=search)
            | Q(booking__studio__studio_name__icontains=search)
        )

    completed_queryset = base_queryset.filter(status='Completed')
    total_amount = completed_queryset.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'payments': payments,
        'total_amount': total_amount,
        'status': status,
        'method': method,
        'search': search,
        'total_payments': base_queryset.count(),
        'completed_count': completed_queryset.count(),
        'processing_count': base_queryset.filter(status='Processing').count(),
        'pending_count': base_queryset.filter(status='Pending').count(),
        'failed_count': base_queryset.filter(status='Failed').count(),
    }
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
    recent_payments = Payment.objects.filter(booking__studio=studio).order_by('-created_at')[:10]

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
def studio_profile(request):
    studio = Studio.objects.filter(user=request.user).first()
    
    if not studio:
        messages.error(request, 'Studio profile not found')
        return redirect('studio_dashboard')

    preferences, _ = StudioPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('studio_profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'studio/dashboard/studio_profile.html', {
        'studio': studio,
        'form': form,
        'user': request.user,
        'preferences': preferences,
    })


@login_required
@role_required(['STUDIO'])
@require_POST
def save_studio_preferences(request):
    preferences, _ = StudioPreference.objects.get_or_create(user=request.user)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'success': False, 'message': 'Invalid JSON payload.'}, status=400)

    preferences.email_notifications = bool(payload.get('email_notifications', preferences.email_notifications))
    preferences.sms_alerts = bool(payload.get('sms_alerts', preferences.sms_alerts))
    preferences.portfolio_visibility = bool(payload.get('portfolio_visibility', preferences.portfolio_visibility))
    preferences.marketing_emails = bool(payload.get('marketing_emails', preferences.marketing_emails))
    preferences.two_factor_enabled = bool(payload.get('two_factor_enabled', preferences.two_factor_enabled))
    preferences.device_login_alerts = bool(payload.get('device_login_alerts', preferences.device_login_alerts))
    preferences.save()

    return JsonResponse({'success': True, 'message': 'Preferences saved successfully.'})


@login_required
@role_required(['STUDIO'])
@require_POST
def logout_all_devices(request):
    current_session_key = request.session.session_key
    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    removed_sessions = 0
    for session in sessions:
        data = session.get_decoded()
        if str(data.get('_auth_user_id')) == str(request.user.id) and session.session_key != current_session_key:
            session.delete()
            removed_sessions += 1

    return JsonResponse({
        'success': True,
        'message': f'Logged out from {removed_sessions} other device(s).'
    })


@login_required
@role_required(['STUDIO'])
@require_POST
def delete_studio_account(request):
    user = request.user
    logout(request)
    user.delete()
    return JsonResponse({'success': True, 'redirect_url': '/'})


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
