from django.contrib import admin
from .models import Airport, AirplaneType, Crew

admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Crew)
