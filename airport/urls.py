from django.urls import path, include
from rest_framework import routers
from .views import AirportViewSet, AirplaneTypeViewSet, CrewViewSet, AirplaneViewSet

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
