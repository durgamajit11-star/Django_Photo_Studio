from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count, Avg
from django.db import transaction
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from accounts.decorators import role_required
from studios.models import Studio
from bookings.models import BookingRequest
from payments.models import Payment
from notifications.models import Notification


User = get_user_model()


@login_required
@role_required(['ADMIN'])
def admin_dashboard(request):
    total_users = User.objects.filter(role='USER').count()
    total_studios = Studio.objects.count()
    total_bookings = BookingRequest.objects.count()

    pending_studios = Studio.objects.filter(is_verified=False).count()
    verified_studios = Studio.objects.filter(is_verified=True).count()
    completed_bookings = BookingRequest.objects.filter(status='Completed').count()
    pending_bookings = BookingRequest.objects.filter(status='Pending').count()
    confirmed_bookings = BookingRequest.objects.filter(status='Confirmed').count()

    total_revenue = BookingRequest.objects.filter(
        status='Confirmed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    avg_booking_value = BookingRequest.objects.filter(status='Confirmed').aggregate(Avg('amount'))['amount__avg'] or 0

    recent_bookings = (
        BookingRequest.objects.select_related('user', 'studio')
        .order_by('-created_at')[:5]
    )

    recent_studios = Studio.objects.select_related('user').order_by('-created_at')[:5]

    top_studios = (
        Studio.objects.annotate(booking_count=Count('booking_requests'))
        .order_by('-booking_count', '-is_verified', '-created_at')[:5]
    )

    payment_snapshot = {
        'completed': Payment.objects.filter(status='Completed').count(),
        'processing': Payment.objects.filter(status='Processing').count(),
        'failed': Payment.objects.filter(status='Failed').count(),
    }

    monthly_revenue = (
        BookingRequest.objects
        .filter(status='Confirmed')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    labels = []
    revenue_data = []
    for item in monthly_revenue:
        labels.append(item['month'].strftime('%b %Y'))
        revenue_data.append(float(item['total']))

    context = {
        'total_users': total_users,
        'total_studios': total_studios,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'avg_booking_value': avg_booking_value,
        'pending_studios': pending_studios,
        'verified_studios': verified_studios,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'recent_bookings': recent_bookings,
        'recent_studios': recent_studios,
        'top_studios': top_studios,
        'payment_snapshot': payment_snapshot,
        'revenue_labels': labels,
        'revenue_data': revenue_data,
    }
    return render(request, 'admin/dashboard/admin_dashboard.html', context)


@login_required
@role_required(['ADMIN'])
def manage_users(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    users = User.objects.filter(role='USER').order_by('-date_joined')
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
        )

    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'blocked':
        users = users.filter(is_active=False)

    return render(
        request,
        'admin/dashboard/manage_users.html',
        {
            'users': users,
            'query': query,
            'status': status,
            'total_users': users.count(),
            'active_users': users.filter(is_active=True).count(),
            'blocked_users': users.filter(is_active=False).count(),
        },
    )


@login_required
@role_required(['ADMIN'])
def manage_admins(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    admins = User.objects.filter(role='ADMIN').order_by('-date_joined')
    if query:
        admins = admins.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
        )

    if status == 'active':
        admins = admins.filter(is_active=True)
    elif status == 'blocked':
        admins = admins.filter(is_active=False)

    return render(
        request,
        'admin/dashboard/manage_admins.html',
        {
            'admins': admins,
            'query': query,
            'status': status,
            'total_admins': admins.count(),
        },
    )


@login_required
@role_required(['ADMIN'])
@require_POST
def toggle_admin_status(request, id):
    admin_user = get_object_or_404(User, id=id, role='ADMIN')

    if admin_user.id == request.user.id:
        messages.error(request, 'You cannot block your own account.')
        return redirect('manage_admins')

    admin_user.is_active = not admin_user.is_active
    admin_user.save(update_fields=['is_active'])
    state = 'unblocked' if admin_user.is_active else 'blocked'
    messages.success(request, f'Admin {admin_user.username} has been {state}.')
    return redirect('manage_admins')


@login_required
@role_required(['ADMIN'])
@require_POST
def toggle_user_status(request, id):
    user = get_object_or_404(User, id=id, role='USER')
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    state = 'unblocked' if user.is_active else 'blocked'
    messages.success(request, f'User {user.username} has been {state}.')
    return redirect('manage_users')


@login_required
@role_required(['ADMIN'])
@require_POST
def delete_user(request, id):
    user = get_object_or_404(User, id=id, role='USER')
    username = user.username
    user.delete()
    messages.success(request, f'User {username} deleted successfully.')
    return redirect('manage_users')


@login_required
@role_required(['ADMIN'])
def manage_studios(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    studios = Studio.objects.select_related('user').order_by('-created_at')
    if query:
        studios = studios.filter(
            Q(studio_name__icontains=query)
            | Q(location__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
        )

    if status == 'verified':
        studios = studios.filter(is_verified=True)
    elif status == 'pending':
        studios = studios.filter(is_verified=False)

    return render(
        request,
        'admin/dashboard/manage_studios.html',
        {
            'studios': studios,
            'query': query,
            'status': status,
            'total_studios': studios.count(),
            'verified_count': studios.filter(is_verified=True).count(),
            'pending_count': studios.filter(is_verified=False).count(),
        },
    )


@login_required
@role_required(['ADMIN'])
@require_POST
def approve_studio(request, id):
    studio = get_object_or_404(Studio, id=id)
    studio.is_verified = True
    studio.save(update_fields=['is_verified'])
    messages.success(request, f'{studio.studio_name} approved successfully.')
    return redirect('manage_studios')


@login_required
@role_required(['ADMIN'])
@require_POST
def reject_studio(request, id):
    studio = get_object_or_404(Studio, id=id)
    studio_name = studio.studio_name
    studio.delete()
    messages.success(request, f'{studio_name} rejected and removed.')
    return redirect('manage_studios')


@login_required
@role_required(['ADMIN'])
@require_POST
def notify_studio(request, id):
    studio = get_object_or_404(Studio.objects.select_related('user'), id=id)
    message_text = (request.POST.get('message') or '').strip()

    if not message_text:
        messages.error(request, 'Notification message is required.')
        return redirect('manage_studios')

    if len(message_text) < 5:
        messages.error(request, 'Notification message is too short (minimum 5 characters).')
        return redirect('manage_studios')

    if len(message_text) > 500:
        messages.error(request, 'Notification message is too long (maximum 500 characters).')
        return redirect('manage_studios')

    Notification.objects.create(
        user=studio.user,
        message=message_text,
        type='admin_notice',
    )
    messages.success(request, f'Notification sent to {studio.studio_name}.')
    return redirect('manage_studios')


@login_required
@role_required(['ADMIN'])
@require_POST
def notify_selected_studios(request):
    message_text = (request.POST.get('message') or '').strip()
    raw_ids = request.POST.getlist('studio_ids')

    if not message_text:
        messages.error(request, 'Notification message is required for bulk send.')
        return redirect('manage_studios')

    if len(message_text) < 5:
        messages.error(request, 'Notification message is too short (minimum 5 characters).')
        return redirect('manage_studios')

    if len(message_text) > 500:
        messages.error(request, 'Notification message is too long (maximum 500 characters).')
        return redirect('manage_studios')

    studio_ids = []
    for value in raw_ids:
        try:
            studio_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    studio_ids = list(set(studio_ids))
    if not studio_ids:
        messages.error(request, 'Please select at least one studio.')
        return redirect('manage_studios')

    target_studios = list(Studio.objects.select_related('user').filter(id__in=studio_ids))
    if not target_studios:
        messages.error(request, 'No valid studios were selected.')
        return redirect('manage_studios')

    payload = [
        Notification(
            user=studio.user,
            message=message_text,
            type='admin_notice',
        )
        for studio in target_studios
    ]

    with transaction.atomic():
        Notification.objects.bulk_create(payload)

    messages.success(request, f'Notification sent to {len(payload)} selected studio(s).')
    return redirect('manage_studios')


@login_required
@role_required(['ADMIN'])
def admin_bookings(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    date = request.GET.get('date', '').strip()

    bookings = BookingRequest.objects.select_related('user', 'studio', 'service').all().order_by('-created_at')
    if query:
        bookings = bookings.filter(
            Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(studio__studio_name__icontains=query)
            | Q(event_type__icontains=query)
        )

    if status:
        bookings = bookings.filter(status=status)

    if date:
        bookings = bookings.filter(date=date)

    confirmed_count = bookings.filter(status='Confirmed').count()
    pending_count = bookings.filter(status='Pending').count()
    cancelled_count = bookings.filter(status='Cancelled').count()

    priority_bookings = []
    stale_pending = []
    now = timezone.now()
    for booking in bookings.filter(status='Pending').select_related('user', 'studio')[:10]:
        age_days = max(0, (now - booking.created_at).days)
        payload = {
            'booking': booking,
            'age_days': age_days,
            'is_urgent': age_days >= 2 or float(booking.amount or 0) >= 10000,
        }
        priority_bookings.append(payload)
        if age_days >= 2:
            stale_pending.append(payload)

    priority_bookings = sorted(priority_bookings, key=lambda item: (not item['is_urgent'], -float(item['booking'].amount or 0), item['age_days']))[:5]

    aging_buckets = {
        '0-1 Days': bookings.filter(status='Pending', created_at__gte=now - timedelta(days=1)).count(),
        '2-3 Days': bookings.filter(status='Pending', created_at__lt=now - timedelta(days=1), created_at__gte=now - timedelta(days=3)).count(),
        '4+ Days': bookings.filter(status='Pending', created_at__lt=now - timedelta(days=3)).count(),
    }
    aging_rows = []
    for label, count in aging_buckets.items():
        percent = int((count / pending_count) * 100) if pending_count else 0
        aging_rows.append({'label': label, 'count': count, 'percent': percent})

    monthly_revenue = (
        BookingRequest.objects
        .filter(status='Confirmed')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    labels = []
    revenue_data = []
    for item in monthly_revenue:
        labels.append(item['month'].strftime('%b %Y'))
        revenue_data.append(float(item['total']))

    context = {
        'bookings': bookings,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
        'priority_bookings': priority_bookings,
        'stale_pending': stale_pending[:5],
        'aging_buckets': aging_buckets,
        'aging_rows': aging_rows,
        'revenue_labels': labels,
        'revenue_data': revenue_data,
        'query': query,
        'status': status,
        'selected_date': date,
    }
    return render(request, 'admin/dashboard/admin_bookings.html', context)


@login_required
@role_required(['ADMIN'])
@require_POST
def admin_cancel_booking(request, id):
    booking = get_object_or_404(BookingRequest, id=id)
    booking.status = 'Cancelled'
    booking.save(update_fields=['status'])
    messages.success(request, f'Booking #{booking.id} has been cancelled.')
    return redirect('admin_bookings')


@login_required
@role_required(['ADMIN'])
def admin_payments(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    method = request.GET.get('method', '').strip()

    payments = Payment.objects.select_related('user', 'booking', 'booking__studio').order_by('-created_at')
    if query:
        payments = payments.filter(
            Q(transaction_id__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(booking__studio__studio_name__icontains=query)
        )

    if status:
        payments = payments.filter(status=status)
    if method:
        payments = payments.filter(payment_method=method)

    stats = {
        'completed_count': payments.filter(status='Completed').count(),
        'pending_count': payments.filter(status='Pending').count(),
        'processing_count': payments.filter(status='Processing').count(),
        'failed_count': payments.filter(status='Failed').count(),
        'total_count': payments.count(),
        'total_amount': payments.filter(status='Completed').aggregate(total=Sum('amount'))['total'] or 0,
    }
    stats['completion_rate'] = int((stats['completed_count'] / stats['total_count']) * 100) if stats['total_count'] else 0

    return render(
        request,
        'admin/dashboard/admin_payments.html',
        {
            'payments': payments,
            'query': query,
            'status': status,
            'method': method,
            'stats': stats,
        },
    )
