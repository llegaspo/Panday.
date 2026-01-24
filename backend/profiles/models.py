from django.db import models
from django.db.models.deletion import CASCADE
from accounts.models import User
from pgvector.django import VectorField, HnswIndex


class Client_Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    client_type = models.CharField(
        max_length=20,
        choices=[
            ("home_owners", "Home Owners"),
            ("construction_firm", "Construction Firm"),
        ],
        default="home_owners",
    )
    company_name = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField()
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    class Meta:
        db_table = "CLIENT_PROFILE"
        verbose_name = "Client Profile"


class Worker_Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    bio_embedding = VectorField(dimensions=1536)
    skill_embedding = VectorField(dimensions=1536)
    is_available = models.BooleanField(default=True)
    availability_radius_km = models.IntegerField(default=2)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
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
            )
        ]
        indexes = [
            HnswIndex(
                name="worker_skill_index",
                fields=["skill_index"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]


class Worker_Verification(models.Model):
    id = models.AutoField(primary_key=True)
    worker_id = models.OneToOneField(Worker_Profile, on_delete=models.CASCADE)
    document_type = models.CharField(
        max_length=20,
        choices=[
            ("national_id", "National ID"),
            ("drivers_license", "Driver's License"),
            ("nbi", "NBI"),
        ],
        default="drivers_license",
    )
    document_url = models.URLField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("reviewing", "Reviewing"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="reviewing",
    )
    reviewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "WORKER_VERIFICATION"
        verbose_name = "Worker Verification"


class Emergency_Contact(models.Model):
    id = models.AutoField(primary_key=True)
    worker_id = models.ForeignKey(Worker_Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=13)
    relationship = models.CharField(
        max_length=10,
        choices=[
            ("mother", "Mother"),
            ("father", "Father"),
            ("sister", "Sister"),
            ("brother", "Brother"),
            ("relatives", "Relatives"),
            ("others", "Others"),
        ],
        blank=True,
    )

    class Meta:
        db_table = "EMERGENCY_CONTACT"
        verbose_name = "Emergency Contact"


class Skill_Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    # for consultation/recommendation engine
    embedding = VectorField(dimensions=1536)

    class Meta:
        db_table = "SKILL_CATEGORY"
        verbose_name = "Skill Category"
        verbose_name = "Skill Categories"

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
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Skill_Category, on_delete=models.CASCADE)
    is_regulated = models.BooleanField(default=False)

    class Meta:
        db_table = "SKILL"
        verbose_name = "Skill"


class Worker_Skill(models.Model):
    id = models.AutoField(primary_key=True)
    worker_id = models.ForeignKey(Worker_Profile, on_delete=models.CASCADE)
    skill = models.OneToOneField(Skill, on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    proof_doc_url = models.URLField()
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "WORKER_SKILL"
        verbose_name = "Worker Skill"
        unique_together = ("worker_id", "skill")


class Consultation(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Client_Profile, on_delete=CASCADE)
    worker_id = models.ForeignKey(Worker_Profile, on_delete=CASCADE)
    # postings from job posting after samatchamakingapp
    status = models.CharField(
        max_length=10,
        choices=[
            ("requested", "Requested"),
            ("scheduled", "Scheduled"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="requested",
    )
    scheduled_at = models.DateTimeField(auto_now_add=True)
    consultation_fee = models.DecimalField(max_digits=7, decimal_places=2, default=0.0)

    class Meta:
        db_table = "CONSULTATION"
        verbose_name = "Consultation"
