from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.dashboard import services


@login_required
def home(request):
    farm = request.farm
    context = {
        "farm": farm,
        "animal_kpis": services.animal_kpis(farm) if farm else None,
        "activities": services.upcoming_activities(farm) if farm else None,
        "performance": services.farm_performance(farm) if farm else None,
        "feed_alerts": services.feed_alerts(farm) if farm else None,
    }
    return render(request, "dashboard/home.html", context)
