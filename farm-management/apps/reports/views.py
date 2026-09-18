from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.dashboard import services
from apps.finance.models import Expense
from apps.sales.models import AnimalSale


@login_required
def summary(request):
    farm = request.farm
    today = date.today()
    context = {
        "farm": farm,
        "animal_kpis": services.animal_kpis(farm) if farm else None,
        "performance": services.farm_performance(farm) if farm else None,
        "recent_sales": AnimalSale.objects.filter(farm=farm).select_related("animal", "buyer")[:15] if farm else [],
        "recent_expenses": Expense.objects.filter(farm=farm)[:15] if farm else [],
        "today": today,
    }
    return render(request, "reports/summary.html", context)
