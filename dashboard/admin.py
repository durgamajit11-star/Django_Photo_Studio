from django.contrib import admin
from .models import StudioPreference, UserPreference

# Studio-related models are registered in the studios app admin


@admin.register(StudioPreference)
class StudioPreferenceAdmin(admin.ModelAdmin):
	list_display = (
		'user',
		'email_notifications',
		'sms_alerts',
		'two_factor_enabled',
		'device_login_alerts',
		'updated_at',
	)
	search_fields = ('user__username', 'user__email')
	list_filter = ('email_notifications', 'sms_alerts', 'two_factor_enabled', 'device_login_alerts')


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
	list_display = (
		'user',
		'email_notifications',
		'sms_alerts',
		'marketing_emails',
		'dark_theme',
		'updated_at',
	)
	search_fields = ('user__username', 'user__email')
	list_filter = ('email_notifications', 'sms_alerts', 'marketing_emails', 'dark_theme')
