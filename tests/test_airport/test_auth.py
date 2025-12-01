from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class JWTAuthenticationTest(TestCase):
    """Test JWT authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_obtain_jwt_token_success(self):
        """Test obtaining JWT token with valid credentials"""
        response = self.client.post("/api/user/token/", {
            "username": "testuser",
            "password": "testpass123"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.assertTrue(len(response.data["access"]) > 0)
        self.assertTrue(len(response.data["refresh"]) > 0)

    def test_obtain_jwt_token_invalid_credentials(self):
        """Test obtaining JWT token with invalid credentials"""
        response = self.client.post("/api/user/token/", {
            "username": "testuser",
            "password": "wrongpassword"
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_jwt_token_missing_fields(self):
        """Test obtaining JWT token with missing fields"""
        response = self.client.post("/api/user/token/", {
            "username": "testuser"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_jwt_token_success(self):
        """Test refreshing JWT token with valid refresh token"""
        obtain_response = self.client.post("/api/user/token/", {
            "username": "testuser",
            "password": "testpass123"
        })
        refresh_token = obtain_response.data["refresh"]

        refresh_response = self.client.post("/api/user/token/refresh/", {
            "refresh": refresh_token
        })

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_refresh_jwt_token_invalid(self):
        """Test refreshing JWT token with invalid refresh token"""
        response = self.client.post("/api/user/token/refresh/", {
            "refresh": "invalid.token.here"
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication"""
        response = self.client.post("/api/booking/orders/", {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        token_response = self.client.post("/api/user/token/", {
            "username": "testuser",
            "password": "testpass123"
        })
        access_token = token_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post("/api/booking/orders/", {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token")
        response = self.client.post("/api/booking/orders/", {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
