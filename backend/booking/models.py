from django.db import models

import uuid
from django.db import models
from django.conf import settings


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        DISPUTED = "DISPUTED", "Disputed"

    class PricingType(models.TextChoices):
        FIXED = "FIXED", "Fixed Price"
        HOURLY = "HOURLY", "Hourly Rate"

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    posting = models.ForeignKey(
        "JobPosting", on_delete=models.SET_NULL, null=True, related_name="bookings"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_bookings",
    )

    total_agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    pricing_type = models.CharField(max_length=20, choices=PricingType.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "BOOKINGS"
        verbose_name = "Booking"
        ordering = ["-start_time"]

    def __str__(self):
        return f"Booking {self.booking_id} - {self.status}"


class JobAssignment(models.Model):
    assignment_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    posting = models.ForeignKey(
        "JobPosting", on_delete=models.CASCADE, related_name="assignments"
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_assignments",
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="assignments",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=100)
    agreed_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="PENDING")

    class Meta:
        db_table = "JOB_ASSIGNMENTS"
        verbose_name = "Job Assignment"

    def __str__(self):
        return f"{self.worker} assigned to {self.posting}"


class BookingParticipant(models.Model):
    participant_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="participants"
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="booking_participations",
    )
    is_lead = models.BooleanField(default=False)
    agreed_share = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Fixed amount or percentage share"
    )
    hours_logged = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, default="ACTIVE")

    class Meta:
        db_table = "BOOKING_PARTICIPANTS"
        verbose_name = "Booking Participant"


class BookingMilestone(models.Model):
    milestone_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="PENDING")
    proof_url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "BOOKING_MILESTONES"
        verbose_name = "Booking Milestone"


class Dispute(models.Model):
    dispute_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="disputes"
    )

    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="raised_disputes",
    )

    reason = models.TextField()
    disputed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DISPUTES"


class Review(models.Model):
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )
    reviewer_role = models.CharField(max_length=50)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "REVIEWS"
        unique_together = ("booking", "reviewer", "reviewee")
