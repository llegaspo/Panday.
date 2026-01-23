from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=75)

    class Meta:
        db_table = "REGIONS"
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"{self.name} (self.code)"


class Province(models.Model):
    id = models.AutoField(primary_key=True)
    region_id = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "PROVINCES"
        verbose_name = "Province"

    def __str__(self):
        return f"{self.name}"


class City(models.Model):
    id = models.AutoField(primary_key=True)
    province_id = models.ForeignKey(Province, on_delete=models.CASCADE)
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
    city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "BARANGAY"
        verbose_name = "Barangay"

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
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
    date_of_birth = models.DateField()
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


class UserAddress(models.Model):
    id = models.AutoField(primary_key=True)

    # A user can have multiple address
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    region_id = models.ForeignKey(Region, on_delete=models.CASCADE)
    province_id = models.ForeignKey(Province, on_delete=models.CASCADE)
    city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    barangay_id = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    longitude = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_primary = models.BooleanField(default=True)
