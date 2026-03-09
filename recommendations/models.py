from django.db import models
from django.conf import settings
from studios.models import Studio


class StudioRecommendation(models.Model):
    """AI-powered studio recommendations for users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studio_recommendations')
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='recommendations')
    
    reason = models.TextField(help_text="Why this studio was recommended")
    score = models.FloatField(default=0.0, help_text="Recommendation score (0-1)")
    
    # User interaction tracking
    seen = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    booked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score', '-created_at']
        unique_together = ['user', 'studio']

    def __str__(self):
        return f"Recommendation for {self.user.username} - {self.studio.studio_name}"


class UserRating(models.Model):
    """Track user preferences and ratings"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_rating')
    
    # Preferences
    preferred_location = models.CharField(max_length=200, blank=True, null=True)
    preferred_studio_type = models.CharField(max_length=100, blank=True, null=True)
    budget_range = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rating profile for {self.user.username}"
