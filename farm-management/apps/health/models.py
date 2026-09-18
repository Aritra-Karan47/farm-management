from django.conf import settings
from django.db import models

from apps.tenants.base_models import FarmScopedModel


class Vaccination(FarmScopedModel):
    animal = models.ForeignKey("animals.Animal", on_delete=models.CASCADE, related_name="vaccinations")
    vaccine = models.CharField(max_length=150)
    date = models.DateField()
    dose = models.CharField(max_length=50, blank=True)
    batch_no = models.CharField(max_length=100, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["farm", "next_due_date"])]

    def __str__(self):
        return f"{self.vaccine} - {self.animal} on {self.date}"


class Deworming(FarmScopedModel):
    animal = models.ForeignKey("animals.Animal", on_delete=models.CASCADE, related_name="dewormings")
    medicine = models.CharField(max_length=150)
    date = models.DateField()
    dose = models.CharField(max_length=50, blank=True)
    body_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["farm", "next_due_date"])]

    def __str__(self):
        return f"{self.medicine} - {self.animal} on {self.date}"


class Treatment(FarmScopedModel):
    animal = models.ForeignKey("animals.Animal", on_delete=models.CASCADE, related_name="treatments")
    date = models.DateField()
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    medicine = models.CharField(max_length=255, blank=True)
    dose = models.CharField(max_length=50, blank=True)
    vet = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    follow_up_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["farm", "follow_up_date"])]

    def __str__(self):
        return f"Treatment - {self.animal} on {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from apps.animals.models import Animal
        Animal.objects.filter(pk=self.animal_id).update(status=Animal.STATUS_SICK)
