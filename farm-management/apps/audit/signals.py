"""
Generic, opt-in audit trail. Rather than hand-writing a signal per model,
each tracked model is registered once here; post_save/post_delete then
write a single AuditLog row using apps.audit.utils.log_action.

This covers the actions Section 20 explicitly calls out: animal created /
updated / sold, vaccination added, expense created, staff deactivated,
purchase created, breeding record updated - and, by being generic, every
other business record too.
"""

from django.db.models.signals import post_delete, post_save

from apps.audit.utils import log_action
from apps.audit.models import AuditLog


def _get_tracked_models():
    from apps.animals.models import Animal, AnimalWeight, AnimalMovement
    from apps.breeding.models import BreedingRecord, KiddingRecord, Kid
    from apps.health.models import Vaccination, Deworming, Treatment
    from apps.feed.models import Feed, FeedConsumption
    from apps.sales.models import AnimalSale, Customer
    from apps.procurement.models import Purchase, Supplier
    from apps.finance.models import Expense
    from apps.staff.models import StaffMembership

    return [
        Animal, AnimalWeight, AnimalMovement,
        BreedingRecord, KiddingRecord, Kid,
        Vaccination, Deworming, Treatment,
        Feed, FeedConsumption,
        AnimalSale, Customer,
        Purchase, Supplier,
        Expense,
        StaffMembership,
    ]


def _on_save(sender, instance, created, **kwargs):
    action = AuditLog.ACTION_CREATE if created else AuditLog.ACTION_UPDATE
    log_action(action, sender._meta.app_label, instance)


def _on_delete(sender, instance, **kwargs):
    log_action(AuditLog.ACTION_DELETE, sender._meta.app_label, instance)


def connect_audit_signals():
    for model in _get_tracked_models():
        post_save.connect(_on_save, sender=model, dispatch_uid=f"audit_save_{model.__name__}")
        post_delete.connect(_on_delete, sender=model, dispatch_uid=f"audit_delete_{model.__name__}")
