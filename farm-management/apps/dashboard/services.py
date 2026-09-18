"""
All dashboard numbers are computed here, directly from the relational
database, so there is exactly one deterministic implementation of each KPI
(Section 24: "AI should never replace deterministic calculations"). The
future AI Farm Assistant will call into these same functions rather than
reimplementing the math.
"""

from datetime import date, timedelta

from django.db.models import Sum

from apps.animals.models import Animal
from apps.breeding.models import BreedingRecord
from apps.feed.models import Feed
from apps.finance.models import Expense
from apps.health.models import Deworming, Treatment, Vaccination
from apps.sales.models import AnimalSale
from apps.breeding.models import KiddingRecord


def animal_kpis(farm):
    qs = Animal.objects.filter(farm=farm)
    return {
        "total": qs.count(),
        "female": qs.filter(gender="FEMALE").exclude(status__in=["SOLD", "DEAD", "CULLED"]).count(),
        "male": qs.filter(gender="MALE").exclude(status__in=["SOLD", "DEAD", "CULLED"]).count(),
        "kids": sum(1 for a in qs.exclude(status__in=["SOLD", "DEAD", "CULLED"]) if a.is_kid),
        "pregnant": qs.filter(status=Animal.STATUS_PREGNANT).count(),
        "sick": qs.filter(status=Animal.STATUS_SICK).count(),
        "quarantine": qs.filter(status=Animal.STATUS_QUARANTINE).count(),
    }


def upcoming_activities(farm, days_ahead=7):
    today = date.today()
    horizon = today + timedelta(days=days_ahead)
    return {
        "vaccinations_due": Vaccination.objects.filter(
            farm=farm, next_due_date__isnull=False, next_due_date__lte=horizon
        ).select_related("animal").order_by("next_due_date")[:20],
        "dewormings_due": Deworming.objects.filter(
            farm=farm, next_due_date__isnull=False, next_due_date__lte=horizon
        ).select_related("animal").order_by("next_due_date")[:20],
        "treatment_followups": Treatment.objects.filter(
            farm=farm, follow_up_date__isnull=False, follow_up_date__lte=horizon
        ).select_related("animal").order_by("follow_up_date")[:20],
        "expected_kiddings": BreedingRecord.objects.filter(
            farm=farm,
            pregnancy_status="CONFIRMED",
            expected_delivery_date__isnull=False,
            expected_delivery_date__lte=horizon,
        ).select_related("female_animal").order_by("expected_delivery_date")[:20],
    }


def farm_performance(farm, month=None, year=None):
    today = date.today()
    month = month or today.month
    year = year or today.year

    kids_born = (
        KiddingRecord.objects.filter(farm=farm, kidding_date__year=year, kidding_date__month=month)
        .aggregate(total=Sum("number_of_kids"))
        .get("total")
        or 0
    )
    kids_sold = AnimalSale.objects.filter(
        farm=farm, sale_date__year=year, sale_date__month=month
    ).count()
    mortality = Animal.objects.filter(
        farm=farm, status=Animal.STATUS_DEAD, updated_at__year=year, updated_at__month=month
    ).count()
    sales_amount = (
        AnimalSale.objects.filter(farm=farm, sale_date__year=year, sale_date__month=month)
        .aggregate(total=Sum("total_amount"))
        .get("total")
        or 0
    )
    expenses_amount = (
        Expense.objects.filter(farm=farm, expense_date__year=year, expense_date__month=month)
        .aggregate(total=Sum("amount"))
        .get("total")
        or 0
    )
    return {
        "kids_born": kids_born,
        "kids_sold": kids_sold,
        "mortality": mortality,
        "sales_this_month": sales_amount,
        "expenses_this_month": expenses_amount,
        "net_profit": sales_amount - expenses_amount,
    }


def feed_alerts(farm):
    return [f for f in Feed.objects.filter(farm=farm) if f.is_below_minimum]
