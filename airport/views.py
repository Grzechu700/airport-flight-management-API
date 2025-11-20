from rest_framework import viewsets
from .models import Airport, AirplaneType, Crew
from .serializers import AirportSerializer, AirplaneTypeSerializer, CrewSerializer


class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
