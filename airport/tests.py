from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Airport


class AirportModelTest(TestCase):
    def test_airport_str(self):
        airport = Airport.objects.create(
            name="Test Airport",
            closest_big_city="Test City",
        )
        self.assertEqual(str(airport), "Test Airport")


class AirportAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_airports(self):
        Airport.objects.create(name="Airport 1", closest_big_city="City 1")
        Airport.objects.create(name="Airport 2", closest_big_city="City 2")

        response = self.client.get("/api/airports/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class JWTAuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_obtain_jwt_token(self):
        response = self.client.post("/api/user/token/", {
            "username": "testuser",
            "password": "testpass123"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
