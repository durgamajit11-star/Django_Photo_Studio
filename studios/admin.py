from django.contrib import admin
from .models import Studio, Portfolio, Review


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('studio_name', 'user', 'location', 'is_featured', 'is_verified', 'average_rating', 'total_bookings', 'created_at')
    list_filter = ('is_featured', 'is_verified', 'created_at', 'updated_at', 'location')
    search_fields = ('studio_name', 'location', 'user__username', 'specializations')
    readonly_fields = ('created_at', 'updated_at', 'average_rating', 'total_bookings', 'confirmed_bookings', 'average_booking_value')
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Studio Details', {'fields': ('studio_name', 'location', 'description', 'profile_image')}),
        ('Contact Information', {'fields': ('phone', 'email', 'website')}),
        ('Business Information', {'fields': ('experience_years', 'specializations', 'price_range')}),
        ('Status', {'fields': ('is_featured', 'is_verified')}),
        ('Analytics', {'fields': ('average_rating', 'total_bookings', 'confirmed_bookings', 'average_booking_value'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def average_rating(self, obj):
        return f"{obj.average_rating():.1f} / 5.0"
    average_rating.short_description = "Average Rating"
    
    def total_bookings(self, obj):
        return obj.total_bookings()
    total_bookings.short_description = "Total Bookings"


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('studio', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at', 'studio')
    search_fields = ('studio__studio_name', 'caption')
    readonly_fields = ('uploaded_at',)
    fieldsets = (
        ('Portfolio Item', {'fields': ('studio', 'image', 'caption')}),
        ('Metadata', {'fields': ('uploaded_at',), 'classes': ('collapse',)}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'studio', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'studio')
    search_fields = ('user__username', 'studio__studio_name', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Review Information', {'fields': ('user', 'studio', 'rating', 'comment')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
