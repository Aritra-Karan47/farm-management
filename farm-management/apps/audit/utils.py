from apps.audit.middleware import get_current_request


def _client_ip(request):
    if not request:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_action(action, module, instance, old_value=None, new_value=None, farm=None):
    """
    Write one AuditLog row. Safe to call from signal handlers - never
    raises, so a logging failure can never break the user-facing action
    being recorded.
    """
    from apps.audit.models import AuditLog

    request = get_current_request()
    user = getattr(request, "user", None) if request else None
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None
    resolved_farm = farm or getattr(instance, "farm", None) or getattr(request, "farm", None)

    try:
        AuditLog.objects.create(
            farm=resolved_farm,
            user=user,
            action=action,
            module=module,
            record_repr=str(instance)[:255],
            record_id=str(getattr(instance, "pk", "")),
            old_value=old_value,
            new_value=new_value,
            ip_address=_client_ip(request),
        )
    except Exception:
        # Auditing must never break the primary operation.
        pass
