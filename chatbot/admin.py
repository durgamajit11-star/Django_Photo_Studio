from django.contrib import admin
from .models import ChatMessage, ChatSession, ChatbotFAQ


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_at_message_time', 'is_user', 'policy_blocked', 'timestamp')
    list_filter = ('timestamp', 'user', 'is_user', 'role_at_message_time', 'policy_blocked')
    search_fields = ('user__username', 'message', 'response', 'user_message', 'bot_response', 'blocked_reason')
    readonly_fields = ('timestamp', 'created_at')
    fieldsets = (
        (
            'Chat',
            {
                'fields': (
                    'user', 'role_at_message_time', 'is_user', 'message', 'response', 'user_message',
                    'bot_response', 'policy_blocked', 'blocked_reason'
                )
            },
        ),
        ('Timestamp', {'fields': ('timestamp', 'created_at'), 'classes': ('collapse',)}),
    )


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'ended', 'created_at')
    list_filter = ('ended', 'created_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at', 'ended_at')
    fieldsets = (
        ('Session', {'fields': ('user', 'title', 'ended')}),
        ('Timestamps', {'fields': ('created_at', 'ended_at'), 'classes': ('collapse',)}),
    )


@admin.register(ChatbotFAQ)
class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'role_scope', 'category', 'active', 'created_at')
    list_filter = ('role_scope', 'category', 'active', 'created_at')
    search_fields = ('question', 'answer', 'keywords')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('FAQ Content', {'fields': ('question', 'answer', 'category', 'role_scope')}),
        ('Settings', {'fields': ('keywords', 'active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
