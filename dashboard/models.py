from django.db import models
from django.conf import settings

# studio model to store studio information and link it to the user
class Studio(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    studio_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="studio_profiles/", blank=True)

    def __str__(self):
        return self.studio_name

# portfolio model to store portfolio items linked to the studio
class Portfolio(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="portfolio/")
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.studio.studio_name} - Portfolio"

# booking model to store booking information linked to the studio
class Booking(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    )

    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    event_type = models.CharField(max_length=100)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Unpaid')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event_type}"

# review model to store reviews linked to the studio
class Review(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Review"

