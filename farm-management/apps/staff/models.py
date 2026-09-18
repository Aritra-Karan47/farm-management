from django.conf import settings
from django.db import models

from apps.tenants.base_models import TimeStampedModel


class StaffMembership(TimeStampedModel):
    """
    Links a User to a Farm with a Role. This is both the "staff" record
    (Section 4 - Add/View/Edit/Activate/Deactivate staff, assign role,
    track joining date) and the RBAC link (a user's permitted farm(s) and
    role on each). Deactivating a staff member never deletes this row -
    historical attribution (who vaccinated an animal, who recorded a sale)
    must survive the person leaving the farm.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="farm_memberships"
    )
    farm = models.ForeignKey(
        "farms.Farm", on_delete=models.CASCADE, related_name="staff_memberships"
    )
    role = models.ForeignKey("accounts.Role", on_delete=models.PROTECT, related_name="memberships")
    staff_code = models.CharField(max_length=30, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-joining_date"]
        unique_together = [("user", "farm")]

    def __str__(self):
        return f"{self.user} @ {self.farm} ({self.role})"
