from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from apps.accounts.models import User, Role


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Farm profile", {"fields": ("phone", "photo")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    filter_horizontal = ("permissions",)
    search_fields = ("code", "name")
