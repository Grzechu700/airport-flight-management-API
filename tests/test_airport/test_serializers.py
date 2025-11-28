from django.test import TestCase
from airport.models import Airport, AirplaneType, Crew, Airplane, Route, Flight
from airport.serializers import (
    AirportSerializer, AirplaneTypeSerializer, CrewSerializer,
    AirplaneSerializer, RouteSerializer, FlightSerializer
)
from django.utils import timezone
from datetime import timedelta


class AirportSerializerTest(TestCase):
    """Test AirportSerializer"""

    def test_airport_serializer_fields(self):
        """Test serializer contains expected fields"""
        airport = Airport.objects.create(
            name="JFK",
            closest_big_city="New York"
        )
        serializer = AirportSerializer(airport)

        self.assertEqual(set(serializer.data.keys()), {"id", "name", "closest_big_city"})
        self.assertEqual(serializer.data["name"], "JFK")
        self.assertEqual(serializer.data["closest_big_city"], "New York")


class AirplaneSerializerTest(TestCase):
    """Test AirplaneSerializer with nested AirplaneType"""

    def test_airplane_serializer_nested_type(self):
        """Test that airplane_type is nested and read-only"""
        airplane_type = AirplaneType.objects.create(name="Boeing 737")
        airplane = Airplane.objects.create(
            name="Test Plane",
            rows=20,
            seats_in_row=6,
            airplane_type=airplane_type
        )

        serializer = AirplaneSerializer(airplane)

        self.assertIn("airplane_type", serializer.data)
        self.assertEqual(serializer.data["airplane_type"]["name"], "Boeing 737")
        self.assertEqual(serializer.data["rows"], 20)
        self.assertEqual(serializer.data["seats_in_row"], 6)


class RouteSerializerTest(TestCase):
    """Test RouteSerializer with nested airports"""

    def test_route_serializer_nested_airports(self):
        """Test that source and destination are nested"""
        airport1 = Airport.objects.create(name="JFK", closest_big_city="NYC")
        airport2 = Airport.objects.create(name="LAX", closest_big_city="LA")
        route = Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=3944
        )

        serializer = RouteSerializer(route)

        self.assertIn("source", serializer.data)
        self.assertIn("destination", serializer.data)
        self.assertEqual(serializer.data["source"]["name"], "JFK")
        self.assertEqual(serializer.data["destination"]["name"], "LAX")
        self.assertEqual(serializer.data["distance"], 3944)


class FlightSerializerTest(TestCase):
    """Test FlightSerializer with nested route, airplane, and crews"""

    def setUp(self):
        airport1 = Airport.objects.create(name="JFK", closest_big_city="NYC")
        airport2 = Airport.objects.create(name="LAX", closest_big_city="LA")
        airplane_type = AirplaneType.objects.create(name="Boeing 737")

        self.airplane = Airplane.objects.create(
            name="Test Plane",
            rows=20,
            seats_in_row=6,
            airplane_type=airplane_type
        )

        self.route = Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=3944
        )

        crew1 = Crew.objects.create(first_name="John", last_name="Pilot")
        crew2 = Crew.objects.create(first_name="Jane", last_name="Attendant")

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=5)
        )
        self.flight.crews.add(crew1, crew2)

    def test_flight_serializer_nested_structure(self):
        """Test all nested relationships in serializer"""
        serializer = FlightSerializer(self.flight)

        self.assertIn("route", serializer.data)
        self.assertEqual(serializer.data["route"]["distance"], 3944)

        self.assertIn("airplane", serializer.data)
        self.assertEqual(serializer.data["airplane"]["name"], "Test Plane")

        self.assertIn("crews", serializer.data)
        self.assertEqual(len(serializer.data["crews"]), 2)
        crew_names = [
            f"{c['first_name']} {c['last_name']}"
            for c in serializer.data["crews"]
        ]
        self.assertIn("John Pilot", crew_names)
        self.assertIn("Jane Attendant", crew_names)
