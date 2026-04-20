from django.contrib import admin
from .models import BookingRequest, BookingNote


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'studio', 'event_type', 'date', 'amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'date', 'created_at', 'studio')
    search_fields = ('user__username', 'studio__studio_name', 'event_type')
    readonly_fields = ('created_at', 'updated_at', 'confirmed_at')
    fieldsets = (
        ('Booking Information', {'fields': ('user', 'studio', 'event_type', 'date', 'start_time', 'end_time', 'time', 'time_slot', 'duration_hours')}),
        ('Location & Requirements', {'fields': ('location', 'special_requirements')}),
        ('Pricing', {'fields': ('amount', 'deposit_amount')}),
        ('Status', {'fields': ('status', 'payment_status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'confirmed_at'), 'classes': ('collapse',)}),
    )


@admin.register(BookingNote)
class BookingNoteAdmin(admin.ModelAdmin):
    list_display = ('booking', 'user', 'created_at')
    list_filter = ('created_at', 'booking')
    search_fields = ('booking__id', 'user__username', 'message')
    readonly_fields = ('created_at',)
