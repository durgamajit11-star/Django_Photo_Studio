from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from bookings.models import BookingRequest
from studios.models import Review, Studio


class UserReviewFlowTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(
			username='reviewer',
			password='Pass123!@#',
			role='USER',
			email='reviewer@example.com',
		)
		self.other_user = user_model.objects.create_user(
			username='otheruser',
			password='Pass123!@#',
			role='USER',
			email='other@example.com',
		)
		self.studio_owner = user_model.objects.create_user(
			username='studioowner',
			password='Pass123!@#',
			role='STUDIO',
			email='studio@example.com',
		)
		self.studio = Studio.objects.create(
			user=self.studio_owner,
			studio_name='Lens House',
			location='Nagpur',
			description='Test studio',
			price_per_hour=1000,
		)

	def _create_booking(self, status='Confirmed'):
		return BookingRequest.objects.create(
			studio=self.studio,
			user=self.user,
			event_type='Wedding',
			date=date.today(),
			booking_date=date.today(),
			amount=2500,
			total_price=2500,
			status=status,
			payment_status='Paid',
		)

	def test_cannot_review_without_confirmed_booking(self):
		self.client.login(username='reviewer', password='Pass123!@#')
		response = self.client.post(
			reverse('add_review', args=[self.studio.id]),
			{'rating': '5', 'comment': 'Great studio'},
		)
		self.assertRedirects(response, reverse('studios:studio_detail', args=[self.studio.id]))
		self.assertEqual(Review.objects.filter(studio=self.studio, user=self.user).count(), 0)

	def test_can_create_review_with_confirmed_booking(self):
		self._create_booking(status='Confirmed')
		self.client.login(username='reviewer', password='Pass123!@#')

		response = self.client.post(
			reverse('add_review', args=[self.studio.id]),
			{'rating': '4', 'comment': 'Nice experience'},
		)

		self.assertRedirects(response, reverse('studios:studio_detail', args=[self.studio.id]))
		review = Review.objects.get(studio=self.studio, user=self.user)
		self.assertEqual(review.rating, 4)
		self.assertEqual(review.comment, 'Nice experience')

	def test_second_post_updates_existing_review(self):
		self._create_booking(status='Completed')
		Review.objects.create(studio=self.studio, user=self.user, rating=3, comment='Old')
		self.client.login(username='reviewer', password='Pass123!@#')

		response = self.client.post(
			reverse('add_review', args=[self.studio.id]),
			{'rating': '5', 'comment': 'Updated review text'},
		)

		self.assertRedirects(response, reverse('studios:studio_detail', args=[self.studio.id]))
		self.assertEqual(Review.objects.filter(studio=self.studio, user=self.user).count(), 1)
		review = Review.objects.get(studio=self.studio, user=self.user)
		self.assertEqual(review.rating, 5)
		self.assertEqual(review.comment, 'Updated review text')

	def test_user_can_edit_and_delete_own_review(self):
		review = Review.objects.create(studio=self.studio, user=self.user, rating=2, comment='Initial')
		self.client.login(username='reviewer', password='Pass123!@#')

		edit_response = self.client.post(
			reverse('edit_review', args=[review.id]),
			{'rating': '4', 'comment': 'Edited text'},
		)
		self.assertRedirects(edit_response, reverse('user_reviews'))

		review.refresh_from_db()
		self.assertEqual(review.rating, 4)
		self.assertEqual(review.comment, 'Edited text')

		delete_response = self.client.post(reverse('delete_review', args=[review.id]))
		self.assertRedirects(delete_response, reverse('user_reviews'))
		self.assertFalse(Review.objects.filter(id=review.id).exists())

	def test_user_cannot_edit_other_users_review(self):
		foreign_review = Review.objects.create(studio=self.studio, user=self.other_user, rating=4, comment='Other review')
		self.client.login(username='reviewer', password='Pass123!@#')

		response = self.client.get(reverse('edit_review', args=[foreign_review.id]))
		self.assertEqual(response.status_code, 404)
