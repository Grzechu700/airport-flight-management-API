from django.contrib import admin
from booking.models import (
    Order,
    Ticket,
)


admin.site.register(Order)
admin.site.register(Ticket)
