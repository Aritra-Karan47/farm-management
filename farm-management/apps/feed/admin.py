from django.contrib import admin
from apps.feed.models import Feed, FeedConsumption


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("feed_name", "farm", "unit", "stock_quantity", "minimum_stock", "is_below_minimum")
    list_filter = ("farm", "unit")
    search_fields = ("feed_name",)

    @admin.display(boolean=True)
    def is_below_minimum(self, obj):
        return obj.is_below_minimum


@admin.register(FeedConsumption)
class FeedConsumptionAdmin(admin.ModelAdmin):
    list_display = ("feed", "date", "quantity", "animal_category", "number_of_animals", "cost", "farm")
    list_filter = ("farm", "animal_category")
    autocomplete_fields = ("feed",)
