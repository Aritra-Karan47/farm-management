from django.contrib import admin
from apps.farms.models import Farm, Location


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization", "status", "created_at")
    list_filter = ("status", "organization")
    search_fields = ("name", "code")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "capacity", "is_active")
    list_filter = ("farm", "is_active")
    search_fields = ("name",)
