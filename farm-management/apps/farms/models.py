from django.db import models

from apps.tenants.base_models import TimeStampedModel


class Farm(TimeStampedModel):
    STATUS_CHOICES = [("ACTIVE", "Active"), ("INACTIVE", "Inactive")]

    organization = models.ForeignKey(
        "tenants.Organization", on_delete=models.CASCADE, related_name="farms"
    )
    name = models.CharField(max_length=255)
    code = models.SlugField(max_length=50, unique=True)
    address = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Location(TimeStampedModel):
    """Shed / pen / paddock within a farm."""

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("farm", "name")]

    def __str__(self):
        return f"{self.name} ({self.farm.name})"
