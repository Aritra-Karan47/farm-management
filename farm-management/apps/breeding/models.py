from django.db import models

from apps.tenants.base_models import FarmScopedModel


class BreedingRecord(FarmScopedModel):
    """Doe -> Heat -> Mating -> (leads to) Pregnancy, per Section 6."""

    MATING_METHOD_CHOICES = [("NATURAL", "Natural"), ("AI", "Artificial Insemination")]
    PREGNANCY_STATUS_CHOICES = [
        ("UNKNOWN", "Unknown / Not confirmed"),
        ("CONFIRMED", "Confirmed Pregnant"),
        ("NOT_PREGNANT", "Not Pregnant"),
        ("DELIVERED", "Delivered"),
        ("ABORTED", "Aborted"),
    ]

    female_animal = models.ForeignKey(
        "animals.Animal", on_delete=models.CASCADE, related_name="breeding_records_as_female",
        limit_choices_to={"gender": "FEMALE"},
    )
    male_animal = models.ForeignKey(
        "animals.Animal", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="breeding_records_as_male", limit_choices_to={"gender": "MALE"},
    )
    heat_date = models.DateField(null=True, blank=True)
    mating_date = models.DateField(null=True, blank=True)
    mating_method = models.CharField(max_length=20, choices=MATING_METHOD_CHOICES, default="NATURAL")
    expected_delivery_date = models.DateField(null=True, blank=True)
    pregnancy_status = models.CharField(
        max_length=20, choices=PREGNANCY_STATUS_CHOICES, default="UNKNOWN"
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-mating_date"]
        indexes = [models.Index(fields=["farm", "pregnancy_status"])]

    def __str__(self):
        return f"Breeding #{self.pk} - {self.female_animal}"

    def save(self, *args, **kwargs):
        # Gestation period for goats is ~150 days; auto-fill the expected
        # delivery date so the dashboard's "Expected Kidding Due" widget
        # works even if the user doesn't type it manually.
        if self.mating_date and not self.expected_delivery_date:
            from datetime import timedelta
            self.expected_delivery_date = self.mating_date + timedelta(days=150)
        super().save(*args, **kwargs)
        if self.pregnancy_status == "CONFIRMED":
            from apps.animals.models import Animal
            Animal.objects.filter(pk=self.female_animal_id).update(status=Animal.STATUS_PREGNANT)


class KiddingRecord(FarmScopedModel):
    breeding_record = models.ForeignKey(
        BreedingRecord, null=True, blank=True, on_delete=models.SET_NULL, related_name="kidding_records"
    )
    female_animal = models.ForeignKey(
        "animals.Animal", on_delete=models.CASCADE, related_name="kidding_records",
        limit_choices_to={"gender": "FEMALE"},
    )
    kidding_date = models.DateField()
    number_of_kids = models.PositiveSmallIntegerField(default=0)
    male_kids = models.PositiveSmallIntegerField(default=0)
    female_kids = models.PositiveSmallIntegerField(default=0)
    birth_assistance = models.CharField(
        max_length=20,
        choices=[("NONE", "None"), ("ASSISTED", "Assisted"), ("VET_ASSISTED", "Vet Assisted")],
        default="NONE",
    )
    complication = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-kidding_date"]

    def __str__(self):
        return f"Kidding #{self.pk} - {self.female_animal} on {self.kidding_date}"

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        from apps.animals.models import Animal
        Animal.objects.filter(pk=self.female_animal_id).update(status=Animal.STATUS_ACTIVE)
        if self.breeding_record_id:
            BreedingRecord.objects.filter(pk=self.breeding_record_id).update(pregnancy_status="DELIVERED")


class Kid(FarmScopedModel):
    """
    Bridge row created for each kid born in a KiddingRecord. On save it
    creates (or links to) the independent Animal record for the kid, so
    the pedigree (Animal.mother / Animal.father) is built automatically as
    required by Section 7.
    """

    kidding_record = models.ForeignKey(KiddingRecord, on_delete=models.CASCADE, related_name="kids")
    animal = models.OneToOneField(
        "animals.Animal", on_delete=models.CASCADE, related_name="kid_record", null=True, blank=True
    )
    tag_no = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[("MALE", "Male"), ("FEMALE", "Female")])
    birth_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["tag_no"]

    def __str__(self):
        return self.tag_no

    def create_animal_record(self, breed):
        """Explicitly create the pedigreed Animal record for this kid."""
        from apps.animals.models import Animal

        if self.animal_id:
            return self.animal
        animal = Animal.objects.create(
            farm=self.farm,
            tag_no=self.tag_no,
            gender=self.gender,
            breed=breed,
            date_of_birth=self.kidding_record.kidding_date,
            mother=self.kidding_record.female_animal,
            father=(
                self.kidding_record.breeding_record.male_animal
                if self.kidding_record.breeding_record_id
                else None
            ),
            birth_weight=self.birth_weight,
            current_weight=self.birth_weight,
            source="BORN_ON_FARM",
            status=Animal.STATUS_ACTIVE,
        )
        self.animal = animal
        self.save(update_fields=["animal"])
        return animal
