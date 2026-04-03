from django.db import models
from django.conf import settings
from studios.models import Studio, Service


class BookingRequest(models.Model):
    """Extended booking request with custom fields"""
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )

    PAYMENT_CHOICES = (
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Refunded', 'Refunded'),
    )

    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='booking_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='booking_requests')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, related_name='bookings', blank=True, null=True)

    event_type = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    booking_date = models.DateField(blank=True, null=True)
    time_slot = models.CharField(max_length=80, blank=True, null=True)
    duration_hours = models.PositiveIntegerField(default=2, help_text="Duration in hours")
    location = models.TextField(blank=True, null=True, help_text="Shooting location")
    special_requirements = models.TextField(blank=True, null=True)
    
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Deposit required")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Unpaid')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking Request'
        verbose_name_plural = 'Booking Requests'

    def __str__(self):
        return f"{self.user.username} - {self.event_type} at {self.studio.studio_name}"

    def save(self, *args, **kwargs):
        # Keep compatibility between older and newer field names.
        if self.booking_date is None and self.date:
            self.booking_date = self.date
        if self.date is None and self.booking_date:
            self.date = self.booking_date
        if self.total_price is None and self.amount is not None:
            self.total_price = self.amount
        if self.amount is None and self.total_price is not None:
            self.amount = self.total_price
        super().save(*args, **kwargs)


class BookingNote(models.Model):
    """Notes/messages for a booking"""
    booking = models.ForeignKey(BookingRequest, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.booking.id} by {self.user.username}"
