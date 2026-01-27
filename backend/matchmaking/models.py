import uuid
from django.db import models
from django.conf import settings


class Trip(models.Model):
    class Status(models.TextChoices):
        EN_ROUTE = "EN_ROUTE", "En Route"
        ARRIVED = "ARRIVED", "Arrived"
        WORKING = "WORKING", "Working"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    trip_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        "Booking", on_delete=models.CASCADE, related_name="trips"
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_trips"
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worker_trips"
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.EN_ROUTE
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "TRIPS"
        verbose_name = "Trip"
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Trip {self.trip_id} ({self.status})"


class LiveLocation(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="locations")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="location_history",
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_m = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "LIVE_LOCATIONS"
        verboce_name = "Live Location"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["trip", "recorded_at"]),
        ]

    def __str__(self):
        return f"{self.user} at {self.recorded_at}"
