from django.core.exceptions import ValidationError
from django.db import models

from Railway_Service_API import settings


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("name",)


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="trains"
    )

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("name",)


class Crew(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("name",)


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return self.name

    @property
    def square(self) -> float:
        return round(self.latitude * self.longitude, 2)

    class Meta:
        ordering = ("name",)


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="routes_from"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="routes_to"
    )
    distance = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.source.name} -> {self.destination.name}"


class Trip(models.Model):
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="trips"
    )
    train = models.ForeignKey(
        Train, on_delete=models.CASCADE, related_name="trips"
    )
    crews = models.ManyToManyField(Crew, related_name="trips", blank=True)

    def __str__(self) -> str:
        return (
            f"Train: {self.train.name}. "
            f"Route: "
            f"{self.route.source.name} -> {self.route.destination.name}. "
            f"Time: {self.departure_time} -> {self.arrival_time}."
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self) -> str:
        return f"Owner: {self.user.username}. Created at: {self.created_at}."

    class Meta:
        ordering = ("-created_at",)


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self) -> str:
        return (
            f"Cargo: {self.cargo}. "
            f"Seat: {self.seat}. "
            f"Train: {self.trip.train.name}."
        )

    @staticmethod
    def validate_ticket(
            cargo: int,
            seat: int,
            train: Train,
            error_to_raise
    ) -> None:
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        Ticket.validate_ticket(
            self.cargo, self.seat, self.trip.train, ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("cargo", "seat", "trip")
        ordering = ("cargo", "seat")
