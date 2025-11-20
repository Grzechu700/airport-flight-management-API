from django.contrib import admin
from .models import Airport, AirplaneType, Crew, Airplane, Route

admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Airplane)
admin.site.register(Route)
