from django.db import models
from accounts.models import User
from pgvector.django import VectorField, HnswIndex


class ClientProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="client_profile"
    )
    CLIENT_TYPES = [
        ("home_owners", "Home Owners"),
        ("construction_firm", "Construction Firm"),
    ]
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPES,
        default="home_owners",
    )
    company_name = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    class Meta:
        db_table = "CLIENT_PROFILE"
        verbose_name = "Client Profile"


class WorkerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="worker_profile"
    )
    bio = models.TextField()
    bio_embedding = VectorField(dimensions=1536)
    skill_embedding = VectorField(dimensions=1536)
    is_available = models.BooleanField(default=True)
    availability_radius_km = models.IntegerField(default=2)
    VERIFICATION_STATUS = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default="pending",
    )
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    class Meta:
        db_table = "WORKER_PROFILE"
        verbose_name = "Worker Profile"
        indexes = [
            HnswIndex(
                name="worker_bio_index",
                fields=["bio_embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
            HnswIndex(
                name="worker_skill_index",
                fields=["skill_embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]


class WorkerVerification(models.Model):
    worker = models.OneToOneField(
        WorkerProfile, on_delete=models.CASCADE, related_name="verification"
    )
    DOC_TYPES = [
        ("national_id", "National ID"),
        ("drivers_license", "Driver's License"),
        ("nbi", "NBI"),
    ]
    document_type = models.CharField(
        max_length=20,
        choices=DOC_TYPES,
        default="drivers_license",
    )
    document_url = models.URLField()
    STATUS_CHOICES = [
        ("reviewing", "Reviewing"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="reviewing",
    )
    reviewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "WORKER_VERIFICATION"
        verbose_name = "Worker Verification"


class EmergencyContact(models.Model):
    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="emergency_contacts"
    )
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=13)

    RELATIONSHIPS = [
        ("mother", "Mother"),
        ("father", "Father"),
        ("sister", "Sister"),
        ("brother", "Brother"),
        ("relatives", "Relatives"),
        ("others", "Others"),
    ]
    relationship = models.CharField(
        max_length=10,
        choices=RELATIONSHIPS,
        blank=True,
    )

    class Meta:
        db_table = "EMERGENCY_CONTACT"
        verbose_name = "Emergency Contact"


class SkillCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    embedding = VectorField(dimensions=1536)

    class Meta:
        db_table = "SKILL_CATEGORY"
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"
        indexes = [
            HnswIndex(
                name="skill_category_index",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]


class Skill(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(
        SkillCategory, on_delete=models.CASCADE, related_name="skills"
    )
    is_regulated = models.BooleanField(default=False)

    class Meta:
        db_table = "SKILL"
        verbose_name = "Skill"


class WorkerSkill(models.Model):
    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="worker_skills"
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="workers_with_skill"
    )

    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    proof_doc_url = models.URLField(blank=True, null=True)  # Likely optional initially
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "WORKER_SKILL"
        verbose_name = "Worker Skill"
        unique_together = (
            "worker",
            "skill",
        )


class Consultation(models.Model):
    client = models.ForeignKey(
        ClientProfile, on_delete=models.CASCADE, related_name="consultations"
    )
    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="consultations"
    )

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="requested",
    )
    scheduled_at = models.DateTimeField(auto_now_add=True)
    consultation_fee = models.DecimalField(max_digits=7, decimal_places=2, default=0.0)

    class Meta:
        db_table = "CONSULTATION"
        verbose_name = "Consultation"
