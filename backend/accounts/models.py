import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import date, timedelta
from django.utils import timezone


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=75)

    class Meta:
        db_table = "REGIONS"
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Province(models.Model):
    id = models.AutoField(primary_key=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "PROVINCES"
        verbose_name = "Province"

    def __str__(self):
        return f"{self.name}"


class City(models.Model):
    id = models.AutoField(primary_key=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    is_major_hub = models.BooleanField(default=False)

    class Meta:
        db_table = "CITIES"
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name} - {self.postal_code}"


class Barangay(models.Model):
    id = models.AutoField(primary_key=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "BARANGAY"
        verbose_name = "Barangay"

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    role = models.CharField(
        max_length=8,
        choices=[
            ("client", "Client"),
            ("worker", "Worker"),
            ("admin", "Admin"),
        ],
        default="worker",
    )
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    total_jobs = models.IntegerField(default=0)

    @property
    def age(self):
        if self.date_of_birth is None:
            return None

        today = date.today()
        age = today.year - self.date_of_birth.year

        if (today.month, today.day) < (
            self.date_of_birth.month,
            self.date_of_birth.day,
        ):
            age -= 1
        return age

    class Meta:
        db_table = "USER"
        verbose_name = "User"


class UserAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    label = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    is_primary = models.BooleanField(default=True)

    class Meta:
        db_table = "ADDRESS"
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


def get_otp_expiry_time():
    return timezone.now() + timedelta(minutes=5)


class OTPVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=100)
    expires_at = models.DateTimeField(default=get_otp_expiry_time)
    verified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "OTP"
        verbose_name = "OTP"


class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_token = models.CharField(max_length=255)
    platform = models.CharField(max_length=10)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "USER_DEVICE"
        verbose_name = "Device"


class UserTrustLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    level = models.CharField(max_length=10)
    score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "TRUST_LEVEL"
        verbose_name = "Trust Level"
