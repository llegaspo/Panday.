import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField  # Requires Postgres
from pgvector.django import VectorField  # Requires pgvector extension


class JobPosting(models.Model):
    class PricingType(models.TextChoices):
        FIXED = "FIXED", "Fixed Price"
        HOURLY = "HOURLY", "Hourly Rate"
        ESTIMATE = "ESTIMATE", "Estimate"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        FILLED = "FILLED", "Filled"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_postings"
    )

    description = models.TextField()
    problem_embedding = VectorField(dimensions=1536, null=True, blank=True)
    image_embedding = VectorField(dimensions=1536, null=True, blank=True)
    media_urls = ArrayField(models.CharField(max_length=500), blank=True, default=list)

    requested_worker_count = models.IntegerField(default=1)
    max_acceptances = models.IntegerField(default=1)

    pricing_type = models.CharField(max_length=20, choices=PricingType.choices)
    min_budget = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    max_budget = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    estimated_duration_hours = models.IntegerField(null=True, blank=True)
    consultation_required = models.BooleanField(default=False)
    location_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    location_long = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "JOB_POSTINGS"
        verbose_name = "Job Posting"

    def __str__(self):
        return f"Job {self.id} ({self.status})"


class JobMediaAnalysis(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    posting = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="media_analyses"
    )

    media_url = models.CharField(max_length=500)
    media_type = models.CharField(max_length=10, choices=MediaType.choices)
    image_embedding = VectorField(dimensions=1536, null=True, blank=True)
    video_embedding = VectorField(dimensions=1536, null=True, blank=True)
    detected_objects = models.JSONField(default=dict, blank=True)
    detected_issues = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "JOB_MEDIA_ANALYSIS"


class AIDecision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context_type = models.CharField(max_length=50)
    context_id = models.UUIDField()
    input_data = models.JSONField()
    output_data = models.JSONField()
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "AI_DECISIONS"
        verbose_name = "AI Decision"
        indexes = [
            models.Index(fields=["context_type", "context_id"]),
        ]


class JobBroadcast(models.Model):
    class BroadcastStatus(models.TextChoices):
        SENT = "SENT", "Sent"
        SEEN = "SEEN", "Seen"
        APPLIED = "APPLIED", "Applied"
        DECLINED = "DECLINED", "Declined"
        EXPIRED = "EXPIRED", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    posting = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="broadcasts"
    )

    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_broadcasts",
    )

    match_score = models.DecimalField(max_digits=5, decimal_places=4)  # e.g., 0.9856

    status = models.CharField(
        max_length=20, choices=BroadcastStatus.choices, default=BroadcastStatus.SENT
    )
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "JOB_BROADCASTS"
        verbose_name = "Job Broadcast"
        unique_together = ("posting", "worker")
