from django.contrib import admin
from apps.animals.models import Species, Breed, Animal, AnimalMovement, AnimalWeight


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("name", "species")
    list_filter = ("species",)
    search_fields = ("name",)


class AnimalWeightInline(admin.TabularInline):
    model = AnimalWeight
    extra = 0
    fields = ("weight_date", "weight_kg", "weight_method", "remarks")
    exclude = ("farm",)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "tag_no", "name", "farm", "gender", "breed", "status",
        "current_weight", "date_of_birth", "location",
    )
    list_filter = ("farm", "gender", "status", "breed", "location")
    search_fields = ("tag_no", "name")
    autocomplete_fields = ("mother", "father", "breed", "location")
    inlines = [AnimalWeightInline]
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            if not obj.farm_id and getattr(request, "farm", None):
                obj.farm = request.farm
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AnimalMovement)
class AnimalMovementAdmin(admin.ModelAdmin):
    list_display = ("animal", "from_location", "to_location", "movement_date")
    list_filter = ("farm",)
    autocomplete_fields = ("animal",)


@admin.register(AnimalWeight)
class AnimalWeightAdmin(admin.ModelAdmin):
    list_display = ("animal", "weight_date", "weight_kg", "weight_method")
    list_filter = ("farm", "weight_method")
    autocomplete_fields = ("animal",)
