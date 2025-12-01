from django.test import TestCase
from django.contrib.auth import get_user_model
from booking.models import Order, Ticket
from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Flight,
)
from django.utils import timezone
from datetime import timedelta


class OrderModelTest(TestCase):
    """Test Order model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="pass123"
        )
        self.order = Order.objects.create(user=self.user)

    def test_order_str(self):
        """Test string representation"""
        expected = f"Order #{self.order.id} by {self.user}"
        self.assertEqual(str(self.order), expected)

    def test_order_created_at_auto(self):
        """Test that created_at is set automatically"""
        self.assertIsNotNone(self.order.created_at)

    def test_order_user_relation(self):
        """Test foreign key relationship with user"""
        self.assertEqual(self.order.user, self.user)
        self.assertIn(self.order, self.user.orders.all())

    def test_order_ordering(self):
        """Test ordering by created_at descending"""
        order2 = Order.objects.create(user=self.user)

        orders = list(Order.objects.all())
        self.assertEqual(orders[0], order2)
        self.assertEqual(orders[1], self.order)


class TicketModelTest(TestCase):
    """Test Ticket model"""

    def setUp(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="pass123"
        )
        self.order = Order.objects.create(user=user)

        airport1 = Airport.objects.create(name="JFK", closest_big_city="NYC")
        airport2 = Airport.objects.create(name="LAX", closest_big_city="LA")
        airplane_type = AirplaneType.objects.create(name="Boeing 737")
        airplane = Airplane.objects.create(
            name="Test Plane",
            rows=20,
            seats_in_row=6,
            airplane_type=airplane_type
        )
        route = Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=3944
        )
        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=5)
        )

        self.ticket = Ticket.objects.create(
            row=5,
            seat=3,
            flight=self.flight,
            order=self.order
        )

    def test_ticket_str(self):
        """Test string representation"""
        expected = f"{self.flight}, {self.ticket.row}, {self.ticket.seat}"
        self.assertEqual(str(self.ticket), expected)

    def test_ticket_relations(self):
        """Test foreign key relationships"""
        self.assertEqual(self.ticket.flight, self.flight)
        self.assertEqual(self.ticket.order, self.order)
        self.assertIn(self.ticket, self.flight.flight_tickets.all())
        self.assertIn(self.ticket, self.order.tickets.all())

    def test_ticket_fields(self):
        """Test ticket fields"""
        self.assertEqual(self.ticket.row, 5)
        self.assertEqual(self.ticket.seat, 3)
