"""
Shared abstract base models.

Every major business record in the platform carries:
    id, farm_id, created_at, updated_at, created_by, updated_by

as required by the platform's database rules. These mixins are imported by
every downstream app so the rule is enforced structurally rather than by
convention.
"""

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserStampedModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated",
    )

    class Meta:
        abstract = True


class FarmScopedModel(TimeStampedModel, UserStampedModel):
    """
    Base class for every farm-owned business record. Guarantees that no
    record can exist without being scoped to a farm, and that every table
    can be filtered by `farm` in a single, consistent way across the whole
    schema (see Section 19 - Multi-Tenant Architecture).
    """

    farm = models.ForeignKey(
        "farms.Farm",
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True
