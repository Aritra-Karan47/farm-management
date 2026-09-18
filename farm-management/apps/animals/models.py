from django.core.validators import MinValueValidator
from django.db import models

from apps.tenants.base_models import FarmScopedModel, TimeStampedModel


class Species(TimeStampedModel):
    """Kept generic (Goat, Sheep, Cattle, ...) so the platform can expand
    beyond goats without a schema change, per Section 3's product boundary."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "species"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Breed(TimeStampedModel):
    species = models.ForeignKey(Species, on_delete=models.PROTECT, related_name="breeds")
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = [("species", "name")]

    def __str__(self):
        return self.name


class Animal(FarmScopedModel):
    GENDER_CHOICES = [("MALE", "Male / Buck"), ("FEMALE", "Female / Doe")]

    STATUS_ACTIVE = "ACTIVE"
    STATUS_PREGNANT = "PREGNANT"
    STATUS_SICK = "SICK"
    STATUS_QUARANTINE = "QUARANTINE"
    STATUS_SOLD = "SOLD"
    STATUS_DEAD = "DEAD"
    STATUS_CULLED = "CULLED"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PREGNANT, "Pregnant"),
        (STATUS_SICK, "Sick"),
        (STATUS_QUARANTINE, "Quarantine"),
        (STATUS_SOLD, "Sold"),
        (STATUS_DEAD, "Dead"),
        (STATUS_CULLED, "Culled"),
    ]

    tag_no = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    breed = models.ForeignKey(Breed, on_delete=models.PROTECT, related_name="animals")
    date_of_birth = models.DateField(null=True, blank=True)
    mother = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="offspring_as_mother"
    )
    father = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="offspring_as_father"
    )
    color = models.CharField(max_length=100, blank=True)
    birth_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    current_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    source = models.CharField(
        max_length=20,
        choices=[("BORN_ON_FARM", "Born on farm"), ("PURCHASED", "Purchased")],
        default="BORN_ON_FARM",
    )
    location = models.ForeignKey(
        "farms.Location", null=True, blank=True, on_delete=models.SET_NULL, related_name="animals"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    photo = models.ImageField(upload_to="animal_photos/", blank=True, null=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["tag_no"]
        constraints = [
            models.UniqueConstraint(fields=["farm", "tag_no"], name="unique_tag_no_per_farm")
        ]
        indexes = [
            models.Index(fields=["farm", "status"]),
            models.Index(fields=["farm", "gender"]),
            models.Index(fields=["farm", "tag_no"]),
        ]

    def __str__(self):
        return f"{self.tag_no} - {self.name}" if self.name else self.tag_no

    @property
    def is_kid(self):
        if not self.date_of_birth:
            return False
        from datetime import date
        age_days = (date.today() - self.date_of_birth).days
        return age_days <= 180  # ~6 months, configurable later

    @property
    def latest_weight_record(self):
        return self.weight_records.order_by("-weight_date").first()

    @property
    def adg(self):
        """Average Daily Gain, computed from the two most recent weight
        records: (current - previous) / days. Returns None if there is
        insufficient history."""
        records = list(self.weight_records.order_by("-weight_date")[:2])
        if len(records) < 2:
            return None
        latest, previous = records
        days = (latest.weight_date - previous.weight_date).days
        if days <= 0:
            return None
        return round((latest.weight_kg - previous.weight_kg) / days, 3)


class AnimalMovement(FarmScopedModel):
    """Tracks shed/location transfers and status transitions for full
    traceability, independent of the audit log (business-meaningful, not
    just technical, history)."""

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="movements")
    from_location = models.ForeignKey(
        "farms.Location", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    to_location = models.ForeignKey(
        "farms.Location", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    movement_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-movement_date"]


class AnimalWeight(FarmScopedModel):
    """Weight history used for growth tracking and ADG calculation
    (Section 9)."""

    METHOD_CHOICES = [("SCALE", "Weighing Scale"), ("TAPE", "Girth Tape"), ("ESTIMATED", "Estimated")]

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="weight_records")
    weight_date = models.DateField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    weight_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="SCALE")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-weight_date"]
        indexes = [models.Index(fields=["animal", "weight_date"])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep the denormalized current_weight on Animal in sync so list
        # views don't need to join/aggregate on every request.
        latest = self.animal.weight_records.order_by("-weight_date").first()
        if latest and self.animal.current_weight != latest.weight_kg:
            Animal.objects.filter(pk=self.animal_id).update(current_weight=latest.weight_kg)

#migration needed
class MilkRecord(FarmScopedModel):
    """Tracks milk yield and quality parameters for each animal."""

    QUALITY_CHOICES = [
        ("GOOD", "Good"),
        ("FAIR", "Fair"),
        ("POOR", "Poor"),
    ]

    METHOD_CHOICES = [
        ("HAND", "Hand Milking"),
        ("MACHINE", "Machine Milking"),
    ]

    SESSION_CHOICES = [
        ("MORNING", "Morning"),
        ("EVENING", "Evening"),
        ("OTHER", "Other"),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="milk_records"
    )
    milking_date = models.DateField()
    milking_time = models.TimeField()
    session = models.CharField(max_length=20, choices=SESSION_CHOICES)
    quantity_liters = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    density = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    snf_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    protein_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    quality_status = models.CharField(max_length=20, choices=QUALITY_CHOICES, blank=True)
    measurement_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="HAND")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-milking_date", "-milking_time"]
        indexes = [
            models.Index(fields=["animal", "milking_date"]),
            models.Index(fields=["farm", "milking_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["animal", "milking_date", "milking_time"],
                name="unique_milk_record_per_session"
            )
        ]

    def __str__(self):
        return f"{self.animal} - {self.milking_date} {self.session}: {self.quantity_liters} L"
