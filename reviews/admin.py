from django.contrib import admin
from .models import ReviewResponse


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ('review', 'studio_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__comment', 'studio_user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Response Information', {'fields': ('review', 'studio_user', 'message')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
