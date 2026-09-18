from django.db import models

from apps.tenants.base_models import FarmScopedModel


class Feed(FarmScopedModel):
    UNIT_CHOICES = [("KG", "Kilogram"), ("BAG", "Bag"), ("LITRE", "Litre")]

    feed_name = models.CharField(max_length=150)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="KG")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.ForeignKey(
        "procurement.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="feeds"
    )
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["feed_name"]
        unique_together = [("farm", "feed_name")]

    def __str__(self):
        return self.feed_name

    @property
    def is_below_minimum(self):
        return self.stock_quantity <= self.minimum_stock


class FeedConsumption(FarmScopedModel):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="consumptions")
    date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    animal_category = models.CharField(
        max_length=20,
        choices=[("ALL", "All"), ("KIDS", "Kids"), ("FEMALE", "Female"), ("MALE", "Male/Buck")],
        default="ALL",
    )
    number_of_animals = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.feed} - {self.quantity}{self.feed.unit} on {self.date}"

    def save(self, *args, **kwargs):
        if not self.cost and self.feed_id:
            self.cost = self.quantity * self.feed.purchase_price
        super().save(*args, **kwargs)
        from django.db.models import F
        Feed.objects.filter(pk=self.feed_id).update(stock_quantity=F("stock_quantity") - self.quantity)
