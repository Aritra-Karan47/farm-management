from django.apps import AppConfig


class AnimalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.animals"

    def ready(self):
        # Ensure Animal has search_fields registered for autocomplete use
        # by other apps' ModelAdmins (breeding, health, sales, etc.)
        pass
