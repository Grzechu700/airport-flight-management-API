from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Route,
)
from .serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    FlightSerializer,
    RouteSerializer,
)


class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirplaneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class FlightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    @action(detail=True, methods=["get"])
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        total_seats = flight.airplane.rows * flight.airplane.seats_in_row
        taken_seats = flight.flight_tickets.count()
        available_seats = total_seats - taken_seats

        return Response({
            "total_seats": total_seats,
            "taken_seats": taken_seats,
            "available_seats": available_seats,
        })
