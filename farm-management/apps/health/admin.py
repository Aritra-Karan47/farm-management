from django.contrib import admin
from apps.health.models import Vaccination, Deworming, Treatment


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ("animal", "vaccine", "date", "next_due_date", "administered_by", "farm")
    list_filter = ("farm", "vaccine")
    autocomplete_fields = ("animal",)
    search_fields = ("vaccine", "animal__tag_no")


@admin.register(Deworming)
class DewormingAdmin(admin.ModelAdmin):
    list_display = ("animal", "medicine", "date", "next_due_date", "administered_by", "farm")
    list_filter = ("farm", "medicine")
    autocomplete_fields = ("animal",)
    search_fields = ("medicine", "animal__tag_no")


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ("animal", "date", "diagnosis", "follow_up_date", "vet", "farm")
    list_filter = ("farm",)
    autocomplete_fields = ("animal",)
    search_fields = ("diagnosis", "animal__tag_no")
