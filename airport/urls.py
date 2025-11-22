from django.urls import path, include
from rest_framework import routers
from .views import (AirportViewSet,
                    AirplaneTypeViewSet,
                    CrewViewSet,
                    AirplaneViewSet,
                    RouteViewSet,
                    FlightViewSet)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
