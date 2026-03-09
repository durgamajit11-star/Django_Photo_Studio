from django.db import models
from django.conf import settings
from studios.models import Studio, Review as StudioReview


class ReviewResponse(models.Model):
    """Studio owner response to a review"""
    review = models.OneToOneField(StudioReview, on_delete=models.CASCADE, related_name='response')
    studio_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Response by {self.studio_user.username}"
