from django.test import TestCase
from airport.models import (
    Airport, AirplaneType, Crew, Airplane, Route, Flight
)
from django.utils import timezone
from datetime import timedelta


class AirportModelTest(TestCase):
    """Test Airport model"""

    def setUp(self):
        self.airport = Airport.objects.create(
            name="John F. Kennedy International",
            closest_big_city="New York"
        )

    def test_airport_str(self):
        """Test string representation"""
        self.assertEqual(str(self.airport), "John F. Kennedy International")

    def test_airport_ordering(self):
        """Test default ordering by name"""
        Airport.objects.create(name="LAX", closest_big_city="Los Angeles")
        Airport.objects.create(name="Airport B", closest_big_city="City B")

        airports = list(Airport.objects.all())
        self.assertEqual(airports[0].name, "Airport B")
        self.assertEqual(airports[1].name, "John F. Kennedy International")
        self.assertEqual(airports[2].name, "LAX")

    def test_airport_fields(self):
        """Test required fields"""
        self.assertEqual(self.airport.name, "John F. Kennedy International")
        self.assertEqual(self.airport.closest_big_city, "New York")


class AirplaneTypeModelTest(TestCase):
    """Test AirplaneType model"""

    def test_airplane_type_str(self):
        airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.assertEqual(str(airplane_type), "Boeing 737")

    def test_airplane_type_ordering(self):
        """Test ordering by name"""
        AirplaneType.objects.create(name="Airbus A320")
        AirplaneType.objects.create(name="Boeing 787")

        types = list(AirplaneType.objects.all())
        self.assertEqual(types[0].name, "Airbus A320")
        self.assertEqual(types[1].name, "Boeing 787")


class CrewModelTest(TestCase):
    """Test Crew model"""

    def test_crew_str(self):
        crew = Crew.objects.create(
            first_name="John",
            last_name="Doe"
        )
        self.assertEqual(str(crew), "John Doe")

    def test_crew_ordering(self):
        """Test ordering by last name"""
        Crew.objects.create(first_name="Alice", last_name="Smith")
        Crew.objects.create(first_name="Bob", last_name="Anderson")

        crew_members = list(Crew.objects.all())
        self.assertEqual(crew_members[0].last_name, "Anderson")
        self.assertEqual(crew_members[1].last_name, "Smith")


class AirplaneModelTest(TestCase):
    """Test Airplane model"""

    def setUp(self):
        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(
            name="Spirit of Freedom",
            rows=30,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )

    def test_airplane_str(self):
        self.assertEqual(str(self.airplane), "Spirit of Freedom")

    def test_airplane_relations(self):
        """Test foreign key relationship"""
        self.assertEqual(self.airplane.airplane_type, self.airplane_type)
        self.assertIn(self.airplane, self.airplane_type.airplanes.all())

    def test_airplane_positive_integers(self):
        """Test that rows and seats_in_row are positive integers"""
        airplane = Airplane.objects.create(
            name="Test Plane",
            rows=10,
            seats_in_row=4,
            airplane_type=self.airplane_type
        )
        self.assertEqual(airplane.rows, 10)
        self.assertEqual(airplane.seats_in_row, 4)


class RouteModelTest(TestCase):
    """Test Route model"""

    def setUp(self):
        self.airport1 = Airport.objects.create(
            name="JFK",
            closest_big_city="New York"
        )
        self.airport2 = Airport.objects.create(
            name="LAX",
            closest_big_city="Los Angeles"
        )
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=3944
        )

    def test_route_str(self):
        self.assertEqual(str(self.route), "JFK -> LAX")

    def test_route_relations(self):
        """Test foreign key relationships"""
        self.assertEqual(self.route.source, self.airport1)
        self.assertEqual(self.route.destination, self.airport2)
        self.assertIn(self.route, self.airport1.routes_as_source.all())
        self.assertIn(self.route, self.airport2.routes_as_destination.all())

    def test_route_ordering(self):
        """Test ordering by source and destination"""
        airport3 = Airport.objects.create(name="ORD", closest_big_city="Chicago")
        route2 = Route.objects.create(
            source=self.airport1,
            destination=airport3,
            distance=1000
        )

        routes = list(Route.objects.all())
        # Should be ordered by source name, then destination name
        self.assertEqual(routes[0], self.route)  # JFK -> LAX
        self.assertEqual(routes[1], route2)  # JFK -> ORD


class FlightModelTest(TestCase):
    """Test Flight model"""

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

        self.crew1 = Crew.objects.create(first_name="John", last_name="Pilot")
        self.crew2 = Crew.objects.create(first_name="Jane", last_name="Attendant")

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=5)
        )
        self.flight.crews.add(self.crew1, self.crew2)

    def test_flight_str(self):
        expected = f"{self.route} -> {self.airplane}"
        self.assertEqual(str(self.flight), expected)

    def test_flight_relations(self):
        """Test foreign key and many-to-many relationships"""
        self.assertEqual(self.flight.route, self.route)
        self.assertEqual(self.flight.airplane, self.airplane)
        self.assertIn(self.crew1, self.flight.crews.all())
        self.assertIn(self.crew2, self.flight.crews.all())
        self.assertEqual(self.flight.crews.count(), 2)

    def test_flight_ordering(self):
        """Test ordering by departure_time"""
        flight2 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=2),
            arrival_time=timezone.now() + timedelta(days=2, hours=5)
        )

        flights = list(Flight.objects.all())
        self.assertEqual(flights[0], self.flight)
        self.assertEqual(flights[1], flight2)
