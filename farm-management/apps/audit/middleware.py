import threading

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


class AuditContextMiddleware:
    """
    Stashes the current request in thread-local storage so that model
    signal handlers (which don't receive the request) can still attribute
    an AuditLog entry to the acting user, farm and IP address.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.request = None
        return response
