from django.db import models
from django.conf import settings

# All studio-related models have been moved to the studios app
# Import them from studios.models if needed


class StudioPreference(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='studio_preference'
	)
	email_notifications = models.BooleanField(default=True)
	sms_alerts = models.BooleanField(default=False)
	portfolio_visibility = models.BooleanField(default=True)
	marketing_emails = models.BooleanField(default=False)
	two_factor_enabled = models.BooleanField(default=False)
	device_login_alerts = models.BooleanField(default=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Studio Preference'
		verbose_name_plural = 'Studio Preferences'

	def __str__(self):
		return f"{self.user.username} studio preferences"

