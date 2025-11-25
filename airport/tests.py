from django.test import TestCase
from .models import Airport


class AirportModelTest(TestCase):
    def test_airport_str(self):
        airport = Airport.objects.create(
            name="Test Airport",
            closest_big_city="Test City",
        )
        self.assertEqual(str(airport), "Test Airport")
