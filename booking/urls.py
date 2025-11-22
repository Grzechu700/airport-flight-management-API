from django.urls import path, include
from rest_framework import routers
from .views import OrderViewSet, TicketViewSet


router = routers.DefaultRouter()
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "booking"