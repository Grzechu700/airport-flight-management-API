from django.contrib import admin
from .models import Airport, AirplaneType, Crew, Airplane, Route, Flight

admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Airplane)
admin.site.register(Route)
admin.site.register(Flight)
