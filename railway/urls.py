from django.urls import path, include
from rest_framework.routers import DefaultRouter

from railway.views import (
    OrderViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
    TripViewSet
)

app_name = "railway"

router = DefaultRouter()

router.register("train_types", TrainTypeViewSet, basename="train_type")
router.register("trains", TrainViewSet, basename="train")
router.register("crews", CrewViewSet, basename="crew")
router.register("stations", StationViewSet, basename="station")
router.register("routes", RouteViewSet, basename="routes")
router.register("trips", TripViewSet, basename="trip")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [path("", include(router.urls))]
