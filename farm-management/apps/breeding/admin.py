from django.contrib import admin
from apps.breeding.models import BreedingRecord, KiddingRecord, Kid


class KidInline(admin.TabularInline):
    model = Kid
    extra = 0
    fields = ("tag_no", "gender", "birth_weight", "animal")
    exclude = ("farm",)


@admin.register(BreedingRecord)
class BreedingRecordAdmin(admin.ModelAdmin):
    list_display = ("female_animal", "male_animal", "mating_date", "expected_delivery_date", "pregnancy_status", "farm")
    list_filter = ("farm", "pregnancy_status", "mating_method")
    autocomplete_fields = ("female_animal", "male_animal")
    search_fields = ("female_animal__tag_no", "male_animal__tag_no")


@admin.register(KiddingRecord)
class KiddingRecordAdmin(admin.ModelAdmin):
    list_display = ("female_animal", "kidding_date", "number_of_kids", "male_kids", "female_kids", "farm")
    list_filter = ("farm",)
    autocomplete_fields = ("female_animal", "breeding_record")
    inlines = [KidInline]
    search_fields = ("female_animal__tag_no",)


@admin.register(Kid)
class KidAdmin(admin.ModelAdmin):
    list_display = ("tag_no", "gender", "kidding_record", "animal")
    autocomplete_fields = ("kidding_record", "animal")
