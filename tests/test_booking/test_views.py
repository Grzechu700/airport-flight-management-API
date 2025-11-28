from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from booking.models import Order, Ticket
from airport.models import Airport, AirplaneType, Airplane, Route, Flight
from django.utils import timezone
from datetime import timedelta


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class OrderViewSetTest(TestCase):
    """Test Order viewset CRUD operations"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="pass123"
        )

    def test_create_order_unauthenticated(self):
        """Test that unauthenticated user cannot create order"""
        response = self.client.post("/api/booking/orders/", {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_authenticated(self):
        """Test that authenticated user can create order"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/booking/orders/", {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user.id)

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)

    def test_list_orders_only_own(self):
        """Test that user can only list their own orders"""
        user2 = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )

        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=user2)

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/booking/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], order1.id)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class TicketViewSetTest(TestCase):
    """Test Ticket viewset CRUD operations"""

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            username="testuser",
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

        self.order = Order.objects.create(user=self.user)

    def test_create_ticket_authenticated(self):
        """Test creating ticket with valid data"""
        self.client.force_authenticate(user=self.user)

        data = {
            "row": 5,
            "seat": 3,
            "flight": self.flight.id,
            "order": self.order.id
        }

        response = self.client.post("/api/booking/tickets/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)

        ticket = Ticket.objects.first()
        self.assertEqual(ticket.row, 5)
        self.assertEqual(ticket.seat, 3)
        self.assertEqual(ticket.flight, self.flight)
        self.assertEqual(ticket.order, self.order)

    def test_create_ticket_unauthenticated(self):
        """Test that unauthenticated user cannot create ticket"""
        data = {
            "row": 5,
            "seat": 3,
            "flight": self.flight.id,
            "order": self.order.id
        }

        response = self.client.post("/api/booking/tickets/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_ticket_invalid_seat(self):
        """Test creating ticket with invalid seat fails"""
        self.client.force_authenticate(user=self.user)

        data = {
            "row": 20,  # Exceeds airplane rows
            "seat": 3,
            "flight": self.flight.id,
            "order": self.order.id
        }

        response = self.client.post("/api/booking/tickets/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_tickets_only_own(self):
        """Test that user can only list tickets from their own orders"""
        user2 = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )
        order2 = Order.objects.create(user=user2)

        ticket1 = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )
        ticket2 = Ticket.objects.create(
            row=1, seat=2, flight=self.flight, order=order2
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/booking/tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], ticket1.id)

    def test_update_ticket_success(self):
        """Test updating ticket to new valid seat"""
        self.client.force_authenticate(user=self.user)

        ticket = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )

        data = {
            "row": 2,
            "seat": 2,
            "flight": self.flight.id,
            "order": self.order.id
        }

        response = self.client.put(f"/api/booking/tickets/{ticket.id}/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.row, 2)
        self.assertEqual(ticket.seat, 2)

    def test_update_ticket_to_occupied_seat_fails(self):
        """Test updating ticket to already occupied seat fails"""
        self.client.force_authenticate(user=self.user)

        ticket1 = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )
        ticket2 = Ticket.objects.create(
            row=2, seat=2, flight=self.flight, order=self.order
        )

        data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order.id
        }

        response = self.client.put(f"/api/booking/tickets/{ticket2.id}/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Seat already booked", str(response.data))

    def test_delete_ticket_success(self):
        """Test deleting ticket"""
        self.client.force_authenticate(user=self.user)

        ticket = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )

        response = self.client.delete(f"/api/booking/tickets/{ticket.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_delete_other_user_ticket_fails(self):
        """Test that user cannot delete another user's ticket"""
        user2 = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )
        order2 = Order.objects.create(user=user2)

        ticket = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=order2
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/booking/tickets/{ticket.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Ticket.objects.count(), 1)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class OrderUpdateDeleteTest(TestCase):
    """Test Order update and delete operations"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="pass123"
        )
        self.order = Order.objects.create(user=self.user)

    def test_update_order_not_allowed(self):
        """Test that updating order is possible but user field is readonly"""
        self.client.force_authenticate(user=self.user)

        user2 = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )

        response = self.client.put(f"/api/booking/orders/{self.order.id}/", {
            "user": user2.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.user, self.user)

    def test_delete_order_success(self):
        """Test deleting order"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f"/api/booking/orders/{self.order.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_other_user_order_fails(self):
        """Test that user cannot delete another user's order"""
        user2 = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )
        order2 = Order.objects.create(user=user2)

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/booking/orders/{order2.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Order.objects.count(), 2)
