from django.db import models

from apps.tenants.base_models import FarmScopedModel


class Customer(FarmScopedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AnimalSale(FarmScopedModel):
    PAYMENT_MODE_CHOICES = [("CASH", "Cash"), ("BANK_TRANSFER", "Bank Transfer"), ("UPI", "UPI"), ("OTHER", "Other")]

    animal = models.OneToOneField("animals.Animal", on_delete=models.PROTECT, related_name="sale_record")
    buyer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="purchases")
    sale_date = models.DateField()
    live_weight = models.DecimalField(max_digits=6, decimal_places=2)
    rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default="CASH")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-sale_date"]

    def __str__(self):
        return f"Sale of {self.animal} to {self.buyer} on {self.sale_date}"

    def save(self, *args, **kwargs):
        self.total_amount = self.live_weight * self.rate_per_kg
        super().save(*args, **kwargs)
        from apps.animals.models import Animal
        Animal.objects.filter(pk=self.animal_id).update(status=Animal.STATUS_SOLD)
