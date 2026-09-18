from django.contrib import admin
from apps.procurement.models import Supplier, Purchase


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "farm")
    search_fields = ("name",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("item_name", "supplier", "purchase_date", "quantity", "unit_price", "total_amount", "payment_status", "farm")
    list_filter = ("farm", "item_type", "payment_status")
    autocomplete_fields = ("supplier",)
    readonly_fields = ("total_amount",)
