from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.tenants.base_models import TimeStampedModel


class User(AbstractUser):
    """
    Custom user model. Kept intentionally close to Django's default so the
    built-in admin, auth views, and permission machinery all work unchanged;
    we only add the fields the farm platform specifically needs.
    """

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="user_photos/", blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.get_full_name() or self.username


class Role(TimeStampedModel):
    """
    A named role (OWNER, ADMIN, FARM_STAFF, VETERINARY, INVENTORY_MANAGER,
    ACCOUNTANT, ...). Wraps Django's built-in Permission model so granular,
    per-action permissions (the `role_permissions` table from Section 17)
    can be attached to a role without inventing a parallel permission
    system.
    """

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    FARM_STAFF = "FARM_STAFF"
    VETERINARY = "VETERINARY"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    ACCOUNTANT = "ACCOUNTANT"

    DEFAULT_ROLE_CHOICES = [
        (OWNER, "Owner"),
        (ADMIN, "Admin"),
        (FARM_STAFF, "Farm Staff"),
        (VETERINARY, "Veterinary"),
        (INVENTORY_MANAGER, "Inventory Manager"),
        (ACCOUNTANT, "Accountant"),
    ]

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        "auth.Permission", blank=True, related_name="farm_roles"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
