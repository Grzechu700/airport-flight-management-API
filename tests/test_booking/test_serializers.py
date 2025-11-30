from django.test import TestCase
from rest_framework.exceptions import ValidationError
from booking.serializers import (
    TicketSerializer,
    OrderSerializer,
)
from booking.models import Order, Ticket
from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Flight,
)
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


class OrderSerializerTest(TestCase):
    """Test OrderSerializer"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="pass123"
        )

    def test_order_serializer_user_readonly(self):
        """Test that user field is read-only"""
        order = Order.objects.create(user=self.user)
        serializer = OrderSerializer(order)

        self.assertIn("user", serializer.data)
        self.assertEqual(serializer.data["user"], self.user.id)

        self.assertIn("user", OrderSerializer.Meta.fields)


class TicketSerializerValidationTest(TestCase):
    """Test suite for TicketSerializer validation logic"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )

        airport1 = Airport.objects.create(name="Airport 1", closest_big_city="City 1")
        airport2 = Airport.objects.create(name="Airport 2", closest_big_city="City 2")
        airplane_type = AirplaneType.objects.create(name="Boeing 737")

        self.airplane = Airplane.objects.create(
            name="Test Airplane",
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
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2)
        )

        self.order = Order.objects.create(user=self.user)

    def test_valid_ticket_creation(self):
        """Test creating ticket with valid row and seat"""
        data = {
            "row": 5,
            "seat": 3,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        ticket = serializer.save()
        self.assertEqual(ticket.row, 5)
        self.assertEqual(ticket.seat, 3)

    def test_row_exceeds_airplane_capacity(self):
        """Test validation fails when row number exceeds airplane rows"""
        data = {
            "row": 11,
            "seat": 3,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("Row 11 does not exist", str(context.exception))

    def test_seat_exceeds_row_capacity(self):
        """Test validation fails when seat number exceeds seats in row"""
        data = {
            "row": 5,
            "seat": 7,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("Seat 7 does not exist", str(context.exception))

    def test_seat_already_booked(self):
        """Test validation fails when seat is already taken"""
        Ticket.objects.create(
            row=5,
            seat=3,
            flight=self.flight,
            order=self.order
        )

        data = {
            "row": 5,
            "seat": 3,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("Seat already booked", str(context.exception))

    def test_update_ticket_same_seat_allowed(self):
        """Test updating ticket to same seat doesn't raise 'already booked' error"""
        ticket = Ticket.objects.create(
            row=5,
            seat=3,
            flight=self.flight,
            order=self.order
        )

        data = {
            "row": 5,
            "seat": 3,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(instance=ticket, data=data)
        self.assertTrue(serializer.is_valid())

    def test_boundary_values_min(self):
        """Test minimum valid values (row=1, seat=1)"""
        data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_boundary_values_max(self):
        """Test maximum valid values"""
        data = {
            "row": 10,
            "seat": 6,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_row_at_exact_limit(self):
        """Test that row equal to airplane rows is valid"""
        data = {
            "row": 10,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_seat_at_exact_limit(self):
        """Test that seat equal to seats_in_row is valid"""
        data = {
            "row": 1,
            "seat": 6,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())


    def test_update_ticket_to_occupied_seat_fails(self):
        """Test updating ticket to already occupied seat fails"""
        ticket1 = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order
        )
        ticket2 = Ticket.objects.create(
            row=2,
            seat=2,
            flight=self.flight,
            order=self.order
        )

        data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order.id
        }
        serializer = TicketSerializer(instance=ticket2, data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("Seat already booked", str(context.exception))
