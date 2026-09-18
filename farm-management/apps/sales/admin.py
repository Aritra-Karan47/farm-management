from django.contrib import admin
from apps.sales.models import Customer, AnimalSale


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "farm")
    search_fields = ("name",)


@admin.register(AnimalSale)
class AnimalSaleAdmin(admin.ModelAdmin):
    list_display = ("animal", "buyer", "sale_date", "live_weight", "rate_per_kg", "total_amount", "payment_mode", "farm")
    list_filter = ("farm", "payment_mode")
    autocomplete_fields = ("animal", "buyer")
    readonly_fields = ("total_amount",)
