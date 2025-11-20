from rest_framework import viewsets
from .models import Airport, AirplaneType, Crew, Airplane, Route
from .serializers import AirportSerializer, AirplaneTypeSerializer, CrewSerializer, AirplaneSerializer, RouteSerializer


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
