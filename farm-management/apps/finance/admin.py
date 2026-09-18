from django.contrib import admin
from apps.finance.models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("category", "description", "amount", "expense_date", "payment_mode", "farm")
    list_filter = ("farm", "category", "payment_mode")
    search_fields = ("description",)
