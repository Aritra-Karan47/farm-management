from django.db import models

from apps.tenants.base_models import FarmScopedModel


class Supplier(FarmScopedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Purchase(FarmScopedModel):
    PAYMENT_STATUS_CHOICES = [("PAID", "Paid"), ("PARTIAL", "Partial"), ("UNPAID", "Unpaid")]

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchases")
    purchase_date = models.DateField()
    item_type = models.CharField(
        max_length=20,
        choices=[("FEED", "Feed"), ("MEDICINE", "Medicine"), ("EQUIPMENT", "Equipment"), ("OTHER", "Other")],
    )
    item_name = models.CharField(max_length=150)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="UNPAID")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-purchase_date"]

    def __str__(self):
        return f"{self.item_name} from {self.supplier} on {self.purchase_date}"

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
