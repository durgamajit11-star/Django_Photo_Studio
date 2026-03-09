from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment, PaymentRefund
from bookings.models import BookingRequest


@login_required
def payment_list(request):
    """Display all payments for the user"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        payments = payments.filter(status=status)
    
    context = {
        'payments': payments,
        'status': status,
    }
    return render(request, 'payments/payment_list.html', context)


@login_required
def create_payment(request, booking_id):
    """Create a payment for a booking"""
    booking = get_object_or_404(BookingRequest, id=booking_id, user=request.user)
    
    # Check if payment already exists
    if hasattr(booking, 'payment'):
        messages.warning(request, 'Payment already exists for this booking')
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if not payment_method:
            messages.error(request, 'Please select a payment method')
            return redirect('create_payment', booking_id=booking_id)
        
        try:
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                amount=booking.amount,
                payment_method=payment_method,
                status='Processing'
            )
            
            # Here you would integrate with a payment gateway
            # For now, we'll mark it as completed
            payment.status = 'Completed'
            payment.transaction_id = f"TXN{payment.id:06d}"
            payment.save()
            
            # Update booking payment status
            booking.payment_status = 'Paid'
            booking.save()
            
            messages.success(request, 'Payment successful!')
            return redirect('payment_detail', payment_id=payment.id)
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('booking_detail', booking_id=booking_id)
    
    context = {'booking': booking}
    return render(request, 'payments/create_payment.html', context)


@login_required
def payment_detail(request, payment_id):
    """Display detailed information about a payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    context = {'payment': payment}
    return render(request, 'payments/payment_detail.html', context)


@login_required
def request_refund(request, payment_id):
    """Request a refund for a payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Check if refund already exists
    if payment.status == 'Refunded':
        messages.warning(request, 'This payment has already been refunded')
        return redirect('payment_detail', payment_id=payment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        amount = request.POST.get('amount', payment.amount)
        
        if not reason:
            messages.error(request, 'Please provide a reason for refund')
            return redirect('request_refund', payment_id=payment_id)
        
        try:
            refund = PaymentRefund.objects.create(
                payment=payment,
                user=request.user,
                reason=reason,
                amount=amount,
                status='Requested'
            )
            messages.success(request, 'Refund request submitted!')
            return redirect('payment_detail', payment_id=payment_id)
        except Exception as e:
            messages.error(request, f'Error submitting refund: {str(e)}')
            return redirect('payment_detail', payment_id=payment_id)
    
    context = {'payment': payment}
    return render(request, 'payments/request_refund.html', context)
