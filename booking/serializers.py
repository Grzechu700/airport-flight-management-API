from rest_framework import serializers
from booking.models import (
    Order,
    Ticket,
)


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

        flight = attrs["flight"]
        row = attrs["row"]
        seat = attrs["seat"]

        if row > flight.airplane.rows:
            raise serializers.ValidationError(
                f"Row {row} does not exist. Airplane has only {flight.airplane.rows} rows."
            )
        if seat > flight.airplane.seats_in_row:
            raise serializers.ValidationError(
                f"Seat {seat} does not exist. Row has only {flight.airplane.seats_in_row} seats."
            )

        queryset = Ticket.objects.filter(
            flight=flight,
            row=row,
            seat=seat,
        )
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Seat already booked")

        return attrs
