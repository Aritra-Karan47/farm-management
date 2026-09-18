from django.db import models

from apps.tenants.base_models import FarmScopedModel


class Expense(FarmScopedModel):
    CATEGORY_CHOICES = [
        ("FEED", "Feed"),
        ("MEDICINE", "Medicine"),
        ("VACCINE", "Vaccine"),
        ("LABOUR", "Labour"),
        ("ELECTRICITY", "Electricity"),
        ("TRANSPORT", "Transport"),
        ("REPAIR", "Repair"),
        ("OTHER", "Other"),
    ]
    PAYMENT_MODE_CHOICES = [("CASH", "Cash"), ("BANK_TRANSFER", "Bank Transfer"), ("UPI", "UPI"), ("OTHER", "Other")]

    expense_date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default="CASH")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-expense_date"]
        indexes = [models.Index(fields=["farm", "category", "expense_date"])]

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount} on {self.expense_date}"
