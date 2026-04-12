from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Studio(models.Model):
    """Model to store studio information and link it to the user"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studio')
    studio_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="studio_profiles/", blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)


    # Advanced Features
    is_featured = models.BooleanField(default=False, help_text="Display on homepage")
    is_verified = models.BooleanField(default=False, help_text="Studio has been verified")
    price_range = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="e.g., $100-$500 per hour"
    )
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of experience")
    specializations = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated specializations"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Studio'
        verbose_name_plural = 'Studios'
        indexes = [
            models.Index(fields=['-is_featured', '-created_at']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return self.studio_name

    def average_rating(self):
        """Calculate average rating for the studio"""
        averages = self.reviews.aggregate(models.Avg('rating'))
        return averages.get('rating__avg') or 0

    def total_bookings(self):
        """Get total number of bookings"""
        from bookings.models import BookingRequest
        return BookingRequest.objects.filter(studio=self).count()

    def confirmed_bookings(self):
        """Get confirmed bookings"""
        from bookings.models import BookingRequest
        return BookingRequest.objects.filter(studio=self, status='Confirmed').count()
    
    def average_booking_value(self):
        """Calculate average booking value"""
        from django.db.models import Avg
        from bookings.models import BookingRequest
        avg = BookingRequest.objects.filter(studio=self, status='Confirmed').aggregate(Avg('amount'))['amount__avg']
        return avg or 0


class Portfolio(models.Model):
    """Model to store portfolio items linked to the studio"""
    CATEGORY_CHOICES = (
        ('wedding', 'Wedding'),
        ('product', 'Product'),
        ('fashion', 'Fashion'),
        ('other', 'Other'),
    )

    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='portfolios')
    image = models.ImageField(upload_to="portfolio/")
    caption = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    tags = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'

    def __str__(self):
        return f"{self.studio.studio_name} - Portfolio"


class StudioImage(models.Model):
    """Dedicated studio image table for gallery/image URLs"""
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='studio_images')
    image = models.ImageField(upload_to="studio_images/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Image for {self.studio.studio_name}"


class Service(models.Model):
    """Services offered by studios (Wedding shoot, Event, etc.)"""
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['studio', 'service_name']
        unique_together = ['studio', 'service_name']

    def __str__(self):
        return f"{self.studio.studio_name} - {self.service_name}"




class Review(models.Model):
    """Model to store reviews linked to the studio"""
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studio_reviews')

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['studio', 'user']  # One review per user per studio
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.user.username} - {self.studio.studio_name} ({self.rating}/5)"
    

