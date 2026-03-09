from rest_framework.routers import DefaultRouter
from .views import (
    StudioViewSet, PortfolioViewSet, ReviewViewSet,
    BookingRequestViewSet, BookingNoteViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'studios', StudioViewSet)
router.register(r'portfolios', PortfolioViewSet)
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'bookings', BookingRequestViewSet, basename='booking')
router.register(r'booking-notes', BookingNoteViewSet, basename='booking-note')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls
