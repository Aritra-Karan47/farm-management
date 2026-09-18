from django.conf import settings
from django.db import models

from apps.tenants.base_models import FarmScopedModel


class Notification(FarmScopedModel):
    TYPE_CHOICES = [
        ("VACCINATION_DUE", "Vaccination Due"),
        ("DEWORMING_DUE", "Deworming Due"),
        ("TREATMENT_FOLLOWUP", "Treatment Follow-up"),
        ("KIDDING_DUE", "Expected Kidding"),
        ("LOW_STOCK", "Low Feed Stock"),
        ("OTHER", "Other"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
