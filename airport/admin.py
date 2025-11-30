from django.contrib import admin
from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Route,
)

admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Airplane)
admin.site.register(Route)
admin.site.register(Flight)
