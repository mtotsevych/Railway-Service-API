from django.db.models import QuerySet, F, Count
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from railway.models import (
    TrainType,
    Train, Crew,
    Station,
    Route,
    Trip,
    Order
)
from railway.paginations import OrderPagination
from railway.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    CrewSerializer,
    StationSerializer,
    RouteDetailSerializer,
    RouteListSerializer,
    TripSerializer,
    TripListSerializer,
    TripDetailSerializer,
    OrderSerializer,
    OrderCreateSerializer,
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("train_type")
        train_name = self.request.query_params.get("name", None)
        if train_name:
            queryset = queryset.filter(name__icontains=train_name)
        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        station_name = self.request.query_params.get("name", None)
        if station_name:
            queryset = queryset.filter(name__icontains=station_name)
        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteListSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("source", "destination")
        return queryset

    def get_serializer_class(self) -> ModelSerializer:
        serializer_class = self.serializer_class
        if self.action == "retrieve":
            return RouteDetailSerializer
        return serializer_class


class TripViewSet(viewsets.ModelViewSet):
    queryset = (
        Trip.objects.all()
        .annotate(
            tickets_available=F("train__cargo_num")
            * F("train__places_in_cargo")
            - Count("tickets")
        )
    )
    serializer_class = TripSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.select_related("route", "train")
        elif self.action == "retrieve":
            queryset = (
                queryset.
                select_related("route", "train").
                prefetch_related("crews")
            )
        route_id = self.request.query_params.get("route", None)
        train_id = self.request.query_params.get("train", None)
        if route_id:
            queryset = queryset.filter(route_id=int(route_id))
        if train_id:
            queryset = queryset.filter(train_id=int(train_id))
        return queryset

    def get_serializer_class(self) -> ModelSerializer:
        serializer_class = self.serializer_class
        if self.action == "list":
            return TripListSerializer
        elif self.action == "retrieve":
            return TripDetailSerializer
        return serializer_class


class OrderViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer: ModelSerializer) -> None:
        serializer.save(user=self.request.user)

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset.filter(user=self.request.user)
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "tickets__trip__route__source",
                "tickets__trip__route__destination",
                "tickets__trip__train",
            )
        return queryset

    def get_serializer_class(self) -> ModelSerializer:
        serializer_class = self.serializer_class
        if self.action == "create":
            return OrderCreateSerializer
        return serializer_class
