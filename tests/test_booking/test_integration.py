from django.test import TestCase
from rest_framework.test import APIClient, override_settings
from rest_framework import status
from django.contrib.auth import get_user_model
from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Flight,
)
from django.utils import timezone
from datetime import timedelta


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class BookingFlowIntegrationTest(TestCase):
    """Test complete booking flow from user creation to ticket booking"""

    def setUp(self):
        self.client = APIClient()

        airport1 = Airport.objects.create(name="JFK", closest_big_city="New York")
        airport2 = Airport.objects.create(name="LAX", closest_big_city="Los Angeles")
        airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(
            name="Test Plane",
            rows=5,
            seats_in_row=4,
            airplane_type=airplane_type
        )
        route = Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=3944
        )
        self.flight = Flight.objects.create(
            route=route,
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=5)
        )

    def test_complete_booking_flow(self):
        """Test complete flow: register -> login -> create order -> book tickets"""
        user = get_user_model().objects.create_user(
            username="traveler",
            password="secure123"
        )

        token_response = self.client.post("/api/user/token/", {
            "username": "traveler",
            "password": "secure123"
        })
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        seats_response = self.client.get(f"/api/flights/{self.flight.id}/available_seats/")
        self.assertEqual(seats_response.status_code, status.HTTP_200_OK)
        self.assertEqual(seats_response.data["available_seats"], 20)

        order_response = self.client.post("/api/booking/orders/", {})
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        order_id = order_response.data["id"]

        ticket1_data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": order_id
        }
        ticket1_response = self.client.post("/api/booking/tickets/", ticket1_data)
        self.assertEqual(ticket1_response.status_code, status.HTTP_201_CREATED)

        ticket2_data = {
            "row": 1,
            "seat": 2,
            "flight": self.flight.id,
            "order": order_id
        }
        ticket2_response = self.client.post("/api/booking/tickets/", ticket2_data)
        self.assertEqual(ticket2_response.status_code, status.HTTP_201_CREATED)

        seats_response2 = self.client.get(f"/api/flights/{self.flight.id}/available_seats/")
        self.assertEqual(seats_response2.data["available_seats"], 18)
        self.assertEqual(seats_response2.data["taken_seats"], 2)

        tickets_response = self.client.get("/api/booking/tickets/")
        self.assertEqual(len(tickets_response.data), 2)

        duplicate_data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": order_id
        }
        duplicate_response = self.client.post("/api/booking/tickets/", duplicate_data)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Seat already booked", str(duplicate_response.data))

    def test_multiple_users_concurrent_booking(self):
        """Test that different users can book different seats on same flight"""
        user1 = get_user_model().objects.create_user(username="user1", password="pass1")
        user2 = get_user_model().objects.create_user(username="user2", password="pass2")

        self.client.force_authenticate(user=user1)
        order1_response = self.client.post("/api/booking/orders/", {})
        order1_id = order1_response.data["id"]

        ticket1_data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": order1_id
        }
        self.client.post("/api/booking/tickets/", ticket1_data)

        self.client.force_authenticate(user=user2)
        order2_response = self.client.post("/api/booking/orders/", {})
        order2_id = order2_response.data["id"]

        ticket2_data = {
            "row": 1,
            "seat": 2,
            "flight": self.flight.id,
            "order": order2_id
        }
        ticket2_response = self.client.post("/api/booking/tickets/", ticket2_data)
        self.assertEqual(ticket2_response.status_code, status.HTTP_201_CREATED)

        ticket3_data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": order2_id
        }
        ticket3_response = self.client.post("/api/booking/tickets/", ticket3_data)
        self.assertEqual(ticket3_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Seat already booked", str(ticket3_response.data))

        self.client.force_authenticate(user=user1)
        user1_tickets = self.client.get("/api/booking/tickets/")
        self.assertEqual(len(user1_tickets.data), 1)

        self.client.force_authenticate(user=user2)
        user2_tickets = self.client.get("/api/booking/tickets/")
        self.assertEqual(len(user2_tickets.data), 1)
