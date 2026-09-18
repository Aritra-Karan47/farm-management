from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """
    Append-only log of important actions. Written by
    apps.audit.utils.log_action(); never edited or deleted through normal
    application code.
    """

    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_OTHER = "OTHER"
    ACTION_CHOICES = [
        (ACTION_CREATE, "Create"),
        (ACTION_UPDATE, "Update"),
        (ACTION_DELETE, "Delete"),
        (ACTION_OTHER, "Other"),
    ]

    farm = models.ForeignKey(
        "farms.Farm", null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    module = models.CharField(max_length=100)
    record_repr = models.CharField(max_length=255)
    record_id = models.CharField(max_length=50, blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["farm", "timestamp"]),
            models.Index(fields=["module", "action"]),
        ]

    def __str__(self):
        return f"[{self.timestamp}] {self.user} {self.action} {self.module}:{self.record_repr}"
