from rest_framework import viewsets
from rest_framework import serializers
from .models import Order, Ticket
from .serializers import OrderSerializer, TicketSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Ticket.objects.filter(order__user=self.request.user)

    def perform_create(self, serializer):
        order_id = self.request.data.get("order")
        if not Order.objects.filter(id=order_id, user=self.request.user).exists():
            raise serializers.ValidationError("You can only create tickets for your own orders")
        serializer.save()
