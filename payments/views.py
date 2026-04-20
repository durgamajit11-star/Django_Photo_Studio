from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
import re
from .models import Payment, PaymentRefund
from bookings.models import BookingRequest


UPI_ID_PATTERN = re.compile(r'^[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}$')
UPI_PAYEE_ID = 'studiosync@upi'
UPI_PAYEE_NAME = 'StudioSync'


def build_upi_payload(amount, booking_id):
    amount_str = f"{Decimal(amount):.2f}"
    note = f"Studio booking #{booking_id}"
    upi_intent = (
        f"upi://pay?pa={quote(UPI_PAYEE_ID)}"
        f"&pn={quote(UPI_PAYEE_NAME)}"
        f"&am={amount_str}"
        f"&cu=INR"
        f"&tn={quote(note)}"
    )
    qr_url = f"https://chart.googleapis.com/chart?cht=qr&chs=360x360&chl={quote(upi_intent, safe='')}"
    return {
        'upi_id': UPI_PAYEE_ID,
        'upi_name': UPI_PAYEE_NAME,
        'upi_intent': upi_intent,
        'upi_qr_url': qr_url,
    }


@login_required
def payment_list(request):
    """Display all payments for the user"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        payments = payments.filter(status=status)

    completed_payments = Payment.objects.filter(user=request.user, status='Completed')
    total_payments = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'payments': payments,
        'status': status,
        'total_payments': total_payments,
        'completed_count': completed_payments.count(),
        'processing_count': Payment.objects.filter(user=request.user, status='Processing').count(),
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

    if booking.status == 'Cancelled':
        messages.error(request, 'Cancelled bookings cannot be paid')
        return redirect('booking_detail', booking_id=booking_id)

    if booking.status != 'Confirmed':
        messages.warning(request, 'Payment is available only after the studio approves your booking.')
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        payer_upi_id = request.POST.get('payer_upi_id', '').strip().lower()
        upi_reference = request.POST.get('upi_reference', '').strip().upper()

        valid_methods = {code for code, _ in Payment.PAYMENT_METHOD_CHOICES}
        
        if not payment_method or payment_method not in valid_methods:
            messages.error(request, 'Please select a payment method')
            return redirect('create_payment', booking_id=booking_id)

        if payment_method == 'UPI':
            if payer_upi_id and not UPI_ID_PATTERN.match(payer_upi_id):
                messages.error(request, 'Please enter a valid UPI ID (example: name@bank)')
                return redirect('create_payment', booking_id=booking_id)

            if not upi_reference or len(upi_reference) < 8:
                messages.error(request, 'Please enter a valid UPI reference/UTR (minimum 8 characters)')
                return redirect('create_payment', booking_id=booking_id)
        
        try:
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                amount=booking.amount,
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

            booking.payment_status = 'Paid'
            booking.save(update_fields=['payment_status', 'updated_at'])

            messages.success(request, 'Payment successful!')
            return redirect('payment_detail', payment_id=payment.id)
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('booking_detail', booking_id=booking_id)

    upi_payload = build_upi_payload(booking.amount, booking.id)
    context = {
        'booking': booking,
        'upi_payload': upi_payload,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'payments/create_payment.html', context)


@login_required
def payment_detail(request, payment_id):
    """Display detailed information about a payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    refunds = payment.refunds.all()
    context = {
        'payment': payment,
        'refunds': refunds,
        'can_request_refund': payment.status == 'Completed',
    }
    return render(request, 'payments/payment_detail.html', context)


@login_required
def request_refund(request, payment_id):
    """Request a refund for a payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Check if refund already exists
    if payment.status == 'Refunded':
        messages.warning(request, 'This payment has already been refunded')
        return redirect('payment_detail', payment_id=payment_id)

    if payment.status != 'Completed':
        messages.error(request, 'Refund can only be requested for completed payments')
        return redirect('payment_detail', payment_id=payment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        amount_raw = request.POST.get('amount', payment.amount)
        
        if not reason:
            messages.error(request, 'Please provide a reason for refund')
            return redirect('request_refund', payment_id=payment_id)

        try:
            amount = Decimal(str(amount_raw))
            if amount <= 0 or amount > payment.amount:
                messages.error(request, 'Refund amount must be greater than 0 and not exceed paid amount')
                return redirect('request_refund', payment_id=payment_id)
        except (InvalidOperation, TypeError):
            messages.error(request, 'Please enter a valid refund amount')
            return redirect('request_refund', payment_id=payment_id)

        existing = PaymentRefund.objects.filter(payment=payment, status__in=['Requested', 'Approved']).exists()
        if existing:
            messages.warning(request, 'A refund request is already in progress for this payment')
            return redirect('payment_detail', payment_id=payment_id)
        
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
