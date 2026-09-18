from django.contrib import admin
from apps.staff.models import StaffMembership


@admin.register(StaffMembership)
class StaffMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "farm", "role", "designation", "joining_date", "is_active")
    list_filter = ("farm", "role", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name", "staff_code")
    autocomplete_fields = ("user",)

    def save_model(self, request, obj, form, change):
        if not obj.is_active and change:
            from django.utils import timezone
            obj.deactivated_at = timezone.now()
        super().save_model(request, obj, form, change)
