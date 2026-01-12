from django.contrib import admin

from railway.models import (
    TrainType,
    Train,
    Crew,
    Station,
    Route,
    Trip,
    Order,
    Ticket
)

admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Crew)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Trip)
admin.site.register(Order)
admin.site.register(Ticket)
