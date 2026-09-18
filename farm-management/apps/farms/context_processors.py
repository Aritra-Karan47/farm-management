def current_farm(request):
    """Expose request.farm to every template as `current_farm`."""
    return {"current_farm": getattr(request, "farm", None)}
