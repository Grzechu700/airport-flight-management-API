from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from booking.models import (
    Order,
    Ticket,
)
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
class OrderPermissionsTest(TestCase):
    """Test Order viewset permissions and filtering"""

    def setUp(self):
        self.client = APIClient()

        self.user1 = get_user_model().objects.create_user(
            username="user1",
            password="pass123"
        )
        self.user2 = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )

        self.order_user1 = Order.objects.create(user=self.user1)
        self.order_user2 = Order.objects.create(user=self.user2)

    def test_user_can_only_see_own_orders(self):
        """Test that user can only see their own orders"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/booking/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order_user1.id)

    def test_user_cannot_access_other_user_order_detail(self):
        """Test that user cannot access another user's order detail"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/booking/orders/{self.order_user2.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_cannot_create_order(self):
        """Test that unauthenticated user cannot create order"""
        response = self.client.post("/api/booking/orders/", {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_create_order(self):
        """Test that authenticated user can create order"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post("/api/booking/orders/", {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user1.id)

    def test_user_auto_assigned_to_order(self):
        """Test that authenticated user is automatically assigned to order"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post("/api/booking/orders/", {})

        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.user, self.user1)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class TicketPermissionsTest(TestCase):
    """Test Ticket viewset permissions and ownership validation"""

    def setUp(self):
        self.client = APIClient()

        self.user1 = get_user_model().objects.create_user(
            username="user1",
            password="pass123"
        )
        self.user2 = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )

        airport1 = Airport.objects.create(name="A1", closest_big_city="C1")
        airport2 = Airport.objects.create(name="A2", closest_big_city="C2")
        airplane_type = AirplaneType.objects.create(name="Boeing")
        airplane = Airplane.objects.create(
            name="Plane1",
            rows=10,
            seats_in_row=6,
            airplane_type=airplane_type
        )
        route = Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=1000
        )
        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2)
        )

        self.order_user1 = Order.objects.create(user=self.user1)
        self.order_user2 = Order.objects.create(user=self.user2)

        self.ticket_user1 = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order_user1
        )
        self.ticket_user2 = Ticket.objects.create(
            row=1,
            seat=2,
            flight=self.flight,
            order=self.order_user2
        )

    def test_user_can_only_see_own_tickets(self):
        """Test that user can only see tickets from their own orders"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/booking/tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.ticket_user1.id)

    def test_user_cannot_create_ticket_for_other_user_order(self):
        """Test that user cannot create ticket for another user's order"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "row": 2,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order_user2.id
        }

        response = self.client.post("/api/booking/tickets/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You can only create tickets for your own orders",
                      str(response.data))

    def test_user_can_create_ticket_for_own_order(self):
        """Test that user can create ticket for their own order"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "row": 2,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order_user1.id
        }

        response = self.client.post("/api/booking/tickets/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_see_other_user_ticket_detail(self):
        """Test that user cannot see detail of another user's ticket"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/booking/tickets/{self.ticket_user2.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
