from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model


class OrderPermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_create_order_without_auth(self):
        """Test that creating order without authentication fails"""
        response = self.client.post("/api/booking/orders/", {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_with_auth(self):
        """Test that creating order with authentication succeeds"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/booking/orders/", {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user.id)
