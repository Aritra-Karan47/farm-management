from django.db import models

from apps.tenants.base_models import TimeStampedModel


class Organization(TimeStampedModel):
    """
    Top-level tenant. A single owner today may only have one Organization
    with one Farm, but the schema supports many farms per organization and
    many organizations on the platform without any migration later.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
