from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import BookingRequest, BookingNote
from studios.models import Studio


@login_required
def booking_list(request):
    """Display all bookings for the current user"""
    bookings = BookingRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(status=status)
    
    context = {
        'bookings': bookings,
        'status': status,
    }
    return render(request, 'bookings/booking_list.html', context)


@login_required
def booking_detail(request, booking_id):
    """Display detailed information about a booking"""
    booking = get_object_or_404(BookingRequest, id=booking_id)
    
    # Check permissions
    if booking.user != request.user and booking.studio.user != request.user:
        messages.error(request, 'You do not have permission to view this booking')
        return redirect('booking_list')
    
    notes = booking.notes.all()
    
    context = {
        'booking': booking,
        'notes': notes,
    }
    return render(request, 'bookings/booking_detail.html', context)


@login_required
def add_note(request, booking_id):
    """Add a note to a booking"""
    booking = get_object_or_404(BookingRequest, id=booking_id)
    
    # Check permissions
    if booking.user != request.user and booking.studio.user != request.user:
        messages.error(request, 'You do not have permission to add notes to this booking')
        return redirect('booking_list')
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            BookingNote.objects.create(
                booking=booking,
                user=request.user,
                message=message
            )
            messages.success(request, 'Note added successfully!')
        return redirect('booking_detail', booking_id=booking_id)
    
    return redirect('booking_detail', booking_id=booking_id)


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(BookingRequest, id=booking_id)
    
    if booking.user != request.user:
        messages.error(request, 'Only the booker can cancel this booking')
        return redirect('booking_list')
    
    if booking.status != 'Pending':
        messages.error(request, 'Only pending bookings can be cancelled')
        return redirect('booking_detail', booking_id=booking_id)
    
    booking.status = 'Cancelled'
    booking.save()
    messages.success(request, 'Booking cancelled successfully!')
    return redirect('booking_detail', booking_id=booking_id)


@login_required
def studio_bookings(request):
    """Display bookings for studio owner"""
    studio = get_object_or_404(Studio, user=request.user)
    bookings = studio.booking_requests.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(status=status)
    
    # Summary stats
    pending = bookings.filter(status='Pending').count()
    confirmed = bookings.filter(status='Confirmed').count()
    
    context = {
        'bookings': bookings,
        'status': status,
        'pending': pending,
        'confirmed': confirmed,
    }
    return render(request, 'bookings/studio_bookings.html', context)


@login_required
def approve_booking(request, booking_id):
    """Approve a booking (studio owner only)"""
    booking = get_object_or_404(BookingRequest, id=booking_id)
    
    if booking.studio.user != request.user:
        messages.error(request, 'You do not have permission to approve this booking')
        return redirect('studio_bookings')
    
    booking.status = 'Confirmed'
    booking.save()
    messages.success(request, 'Booking approved successfully!')
    return redirect('booking_detail', booking_id=booking_id)


@login_required
def reject_booking(request, booking_id):
    """Reject a booking (studio owner only)"""
    booking = get_object_or_404(BookingRequest, id=booking_id)
    
    if booking.studio.user != request.user:
        messages.error(request, 'You do not have permission to reject this booking')
        return redirect('studio_bookings')
    
    booking.status = 'Cancelled'
    booking.save()
    messages.success(request, 'Booking rejected!')
    return redirect('booking_detail', booking_id=booking_id)
