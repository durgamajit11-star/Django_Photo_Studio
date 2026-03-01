from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('USER', 'User'),
        ('STUDIO', 'Studio'),
        ('ADMIN', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='USER'   # 🔥 important default
    )

    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # ===== Studio Fields (optional but future ready) =====
    studio_name = models.CharField(max_length=200, blank=True, null=True)
    owner_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    license = models.FileField(upload_to='licenses/', blank=True, null=True)
    portfolio = models.FileField(upload_to='portfolios/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Automatically assign ADMIN role to superuser
        if self.is_superuser:
            self.role = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.role}"