from rest_framework import serializers
from .models import Order, Ticket


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "user"
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "order",
        )

    def validate(self, attrs):
        attrs = super(TicketSerializer, self).validate(attrs)
        if Ticket.objects.filter(
            flight=attrs["flight"],
            row=attrs["row"],
            seat=attrs["seat"],
        ).exists():
            raise serializers.ValidationError("Seat already booked")
        return attrs
