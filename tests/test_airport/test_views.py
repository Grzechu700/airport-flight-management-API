from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import Airport, AirplaneType, Crew, Airplane, Route, Flight
from booking.models import Order, Ticket
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class AirportViewSetTest(TestCase):
    """Test Airport ReadOnly ViewSet"""

    def setUp(self):
        self.client = APIClient()
        Airport.objects.create(name="JFK", closest_big_city="New York")
        Airport.objects.create(name="LAX", closest_big_city="Los Angeles")

    def test_list_airports(self):
        """Test listing all airports"""
        response = self.client.get("/api/airports/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_airport(self):
        """Test retrieving single airport"""
        airport = Airport.objects.first()
        response = self.client.get(f"/api/airports/{airport.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], airport.name)

    def test_create_airport_not_allowed(self):
        """Test that creating airport is not allowed (ReadOnly)"""
        response = self.client.post("/api/airports/", {
            "name": "ORD",
            "closest_big_city": "Chicago"
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_airport_not_allowed(self):
        """Test that updating airport is not allowed"""
        airport = Airport.objects.first()
        response = self.client.put(f"/api/airports/{airport.id}/", {
            "name": "Updated",
            "closest_big_city": "Updated City"
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_airport_not_allowed(self):
        """Test that deleting airport is not allowed"""
        airport = Airport.objects.first()
        response = self.client.delete(f"/api/airports/{airport.id}/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class FlightViewSetTest(TestCase):
    """Test Flight ReadOnly ViewSet and custom actions"""

    def setUp(self):
        self.client = APIClient()

        airport1 = Airport.objects.create(name="JFK", closest_big_city="NYC")
        airport2 = Airport.objects.create(name="LAX", closest_big_city="LA")
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

        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="pass123"
        )
        self.order = Order.objects.create(user=self.user)

    def test_list_flights(self):
        """Test listing all flights"""
        response = self.client.get("/api/flights/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_flight_with_nested_data(self):
        """Test that flight detail includes nested route, airplane, crews"""
        response = self.client.get(f"/api/flights/{self.flight.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("route", response.data)
        self.assertIn("airplane", response.data)
        self.assertIn("crews", response.data)

    def test_available_seats_no_bookings(self):
        """Test available_seats action with no tickets booked"""
        response = self.client.get(f"/api/flights/{self.flight.id}/available_seats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_seats"], 20)
        self.assertEqual(response.data["taken_seats"], 0)
        self.assertEqual(response.data["available_seats"], 20)

    def test_available_seats_with_bookings(self):
        """Test available_seats action with some tickets booked"""
        Ticket.objects.create(row=1, seat=1, flight=self.flight, order=self.order)
        Ticket.objects.create(row=1, seat=2, flight=self.flight, order=self.order)
        Ticket.objects.create(row=2, seat=1, flight=self.flight, order=self.order)

        response = self.client.get(f"/api/flights/{self.flight.id}/available_seats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_seats"], 20)
        self.assertEqual(response.data["taken_seats"], 3)
        self.assertEqual(response.data["available_seats"], 17)

    def test_available_seats_fully_booked(self):
        """Test available_seats when flight is fully booked"""
        for row in range(1, 6):
            for seat in range(1, 5):
                Ticket.objects.create(
                    row=row,
                    seat=seat,
                    flight=self.flight,
                    order=self.order
                )

        response = self.client.get(f"/api/flights/{self.flight.id}/available_seats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_seats"], 20)
        self.assertEqual(response.data["taken_seats"], 20)
        self.assertEqual(response.data["available_seats"], 0)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class RouteViewSetTest(TestCase):
    """Test Route ReadOnly ViewSet"""

    def setUp(self):
        self.client = APIClient()
        airport1 = Airport.objects.create(name="JFK", closest_big_city="NYC")
        airport2 = Airport.objects.create(name="LAX", closest_big_city="LA")
        Route.objects.create(source=airport1, destination=airport2, distance=3944)

    def test_list_routes(self):
        """Test listing routes"""
        response = self.client.get("/api/routes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_route_with_nested_airports(self):
        """Test route detail includes nested source and destination"""
        route = Route.objects.first()
        response = self.client.get(f"/api/routes/{route.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("source", response.data)
        self.assertIn("destination", response.data)
        self.assertEqual(response.data["source"]["name"], "JFK")
        self.assertEqual(response.data["destination"]["name"], "LAX")


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class AirplaneTypeViewSetTest(TestCase):
    """Test AirplaneType ReadOnly ViewSet"""

    def setUp(self):
        self.client = APIClient()
        AirplaneType.objects.create(name="Boeing 737")
        AirplaneType.objects.create(name="Airbus A320")

    def test_list_airplane_types(self):
        """Test listing all airplane types"""
        response = self.client.get("/api/airplane-types/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_airplane_type(self):
        """Test retrieving single airplane type"""
        airplane_type = AirplaneType.objects.first()
        response = self.client.get(f"/api/airplane-types/{airplane_type.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], airplane_type.name)

    def test_create_airplane_type_not_allowed(self):
        """Test that creating airplane type is not allowed (ReadOnly)"""
        response = self.client.post("/api/airplane-types/", {
            "name": "Boeing 777"
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_airplane_type_not_allowed(self):
        """Test that updating airplane type is not allowed"""
        airplane_type = AirplaneType.objects.first()
        response = self.client.put(f"/api/airplane-types/{airplane_type.id}/", {
            "name": "Updated Type"
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_airplane_type_not_allowed(self):
        """Test that deleting airplane type is not allowed"""
        airplane_type = AirplaneType.objects.first()
        response = self.client.delete(f"/api/airplane-types/{airplane_type.id}/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class CrewViewSetTest(TestCase):
    """Test Crew ReadOnly ViewSet"""

    def setUp(self):
        self.client = APIClient()
        Crew.objects.create(first_name="John", last_name="Pilot")
        Crew.objects.create(first_name="Jane", last_name="Attendant")

    def test_list_crew_members(self):
        """Test listing all crew members"""
        response = self.client.get("/api/crews/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_crew_member(self):
        """Test retrieving single crew member"""
        crew = Crew.objects.first()
        response = self.client.get(f"/api/crews/{crew.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], crew.first_name)
        self.assertEqual(response.data["last_name"], crew.last_name)

    def test_create_crew_not_allowed(self):
        """Test that creating crew is not allowed (ReadOnly)"""
        response = self.client.post("/api/crews/", {
            "first_name": "Bob",
            "last_name": "Smith"
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_crew_not_allowed(self):
        """Test that updating crew is not allowed"""
        crew = Crew.objects.first()
        response = self.client.put(f"/api/crews/{crew.id}/", {
            "first_name": "Updated",
            "last_name": "Name"
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_crew_not_allowed(self):
        """Test that deleting crew is not allowed"""
        crew = Crew.objects.first()
        response = self.client.delete(f"/api/crews/{crew.id}/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class AirplaneViewSetTest(TestCase):
    """Test Airplane ReadOnly ViewSet"""

    def setUp(self):
        self.client = APIClient()
        airplane_type = AirplaneType.objects.create(name="Boeing 737")
        Airplane.objects.create(
            name="Plane 1",
            rows=20,
            seats_in_row=6,
            airplane_type=airplane_type
        )
        Airplane.objects.create(
            name="Plane 2",
            rows=30,
            seats_in_row=8,
            airplane_type=airplane_type
        )

    def test_list_airplanes(self):
        """Test listing all airplanes"""
        response = self.client.get("/api/airplanes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_airplane_with_nested_type(self):
        """Test retrieving single airplane with nested type"""
        airplane = Airplane.objects.first()
        response = self.client.get(f"/api/airplanes/{airplane.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], airplane.name)
        self.assertIn("airplane_type", response.data)
        self.assertEqual(response.data["airplane_type"]["name"], "Boeing 737")

    def test_create_airplane_not_allowed(self):
        """Test that creating airplane is not allowed (ReadOnly)"""
        airplane_type = AirplaneType.objects.first()
        response = self.client.post("/api/airplanes/", {
            "name": "New Plane",
            "rows": 25,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_airplane_not_allowed(self):
        """Test that updating airplane is not allowed"""
        airplane = Airplane.objects.first()
        response = self.client.put(f"/api/airplanes/{airplane.id}/", {
            "name": "Updated Plane",
            "rows": 30,
            "seats_in_row": 8,
            "airplane_type": airplane.airplane_type.id
        })

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_airplane_not_allowed(self):
        """Test that deleting airplane is not allowed"""
        airplane = Airplane.objects.first()
        response = self.client.delete(f"/api/airplanes/{airplane.id}/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class UnauthenticatedAccessTest(TestCase):
    """Test unauthenticated access to read-only endpoints"""

    def setUp(self):
        self.client = APIClient()

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
        crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=5)
        )
        self.flight.crews.add(crew)

    def test_unauthenticated_can_list_airports(self):
        """Test that unauthenticated users can list airports"""
        response = self.client.get("/api/airports/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_retrieve_airport(self):
        """Test that unauthenticated users can retrieve airport"""
        airport = Airport.objects.first()
        response = self.client.get(f"/api/airports/{airport.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_list_flights(self):
        """Test that unauthenticated users can list flights"""
        response = self.client.get("/api/flights/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_retrieve_flight(self):
        """Test that unauthenticated users can retrieve flight"""
        response = self.client.get(f"/api/flights/{self.flight.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_access_available_seats(self):
        """Test that unauthenticated users can access available_seats action"""
        response = self.client.get(f"/api/flights/{self.flight.id}/available_seats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("available_seats", response.data)

    def test_unauthenticated_can_list_routes(self):
        """Test that unauthenticated users can list routes"""
        response = self.client.get("/api/routes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_list_airplane_types(self):
        """Test that unauthenticated users can list airplane types"""
        response = self.client.get("/api/airplane-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_list_crews(self):
        """Test that unauthenticated users can list crews"""
        response = self.client.get("/api/crews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_list_airplanes(self):
        """Test that unauthenticated users can list airplanes"""
        response = self.client.get("/api/airplanes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
