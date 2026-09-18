"""
CurrentFarmMiddleware resolves the authenticated user's permitted farm and
attaches it to the request as `request.farm`. Every view / queryset in the
project must scope through `request.farm` rather than trusting any farm_id
supplied by the client, per Section 19 of the spec:

    Never trust farm_id sent directly from frontend JavaScript.
"""


class CurrentFarmMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.farm = None
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            # Superusers/owners may have access to multiple farms; default
            # to their primary farm membership. Staff have exactly one.
            membership = user.farm_memberships.filter(is_active=True).select_related("farm").first()
            if membership:
                request.farm = membership.farm
        response = self.get_response(request)
        return response
