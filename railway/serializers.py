from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from railway.models import (
    TrainType,
    Train,
    Station,
    Route,
    Trip,
    Crew,
    Order,
    Ticket
)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name",)


class TrainSerializer(serializers.ModelSerializer):
    train_type = SlugRelatedField(
        many=False,
        read_only=False,
        queryset=TrainType.objects.all(),
        slug_field="name",
    )

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "capacity",
            "train_type",
        )


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude", "square",)


class RouteListSerializer(serializers.ModelSerializer):
    source = SlugRelatedField(
        many=False,
        read_only=False,
        queryset=Station.objects.all(),
        slug_field="name",
    )
    destination = SlugRelatedField(
        many=False,
        read_only=False,
        queryset=Station.objects.all(),
        slug_field="name",
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class RouteDetailSerializer(RouteListSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "name",)


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "train",
            "crews"
        )


class TripListSerializer(serializers.ModelSerializer):
    departure_station = serializers.CharField(
        source="route.source.name", read_only=True
    )
    arrival_station = serializers.CharField(
        source="route.destination.name", read_only=True
    )
    train_name = serializers.CharField(source="train.name", read_only=True)
    train_capacity = serializers.IntegerField(
        source="train.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "departure_station",
            "arrival_station",
            "train_name",
            "train_capacity",
            "tickets_available",
            "departure_time",
            "arrival_time",
        )


class TicketSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat",)


class TripDetailSerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField(read_only=True)
    route = RouteDetailSerializer(many=False, read_only=True)
    train = TrainSerializer(many=False, read_only=True)
    crews = SlugRelatedField(
        many=True, read_only=True, slug_field="name",
    )
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Trip
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "tickets_available",
            "taken_places",
            "route",
            "train",
            "crews"
        )


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "cargo",
            "seat",
            "trip",
        )

    def validate(self, attrs: dict) -> dict:
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["trip"].train,
            ValidationError
        )
        return attrs


class TicketSerializer(serializers.ModelSerializer):
    trip = TripListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "cargo",
            "seat",
            "trip",
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(
        many=True, read_only=False, allow_empty=False
    )

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    @transaction.atomic
    def create(self, validated_data: dict) -> Order:
        tickets = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket in tickets:
            Ticket.objects.create(order=order, **ticket)
        return order


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")
