from django.contrib import admin
from .models import StudioRecommendation, UserRating


@admin.register(StudioRecommendation)
class StudioRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'studio', 'score', 'seen', 'clicked', 'booked', 'created_at')
    list_filter = ('seen', 'clicked', 'booked', 'created_at')
    search_fields = ('user__username', 'studio__studio_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Recommendation', {'fields': ('user', 'studio', 'reason', 'score')}),
        ('Interactions', {'fields': ('seen', 'clicked', 'booked')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_location', 'budget_range', 'created_at')
    list_filter = ('created_at', 'preferred_location')
    search_fields = ('user__username', 'preferred_location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Preferences', {'fields': ('user', 'preferred_location', 'preferred_studio_type', 'budget_range')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
