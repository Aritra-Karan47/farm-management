from django.contrib import admin
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "notification_type", "due_date", "is_read", "farm")
    list_filter = ("farm", "notification_type", "is_read")
