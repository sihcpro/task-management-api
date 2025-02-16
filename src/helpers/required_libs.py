class NoClass:
    pass


try:
    from rest_framework.request import Request
except ImportError:
    Request = NoClass


__all__ = ["Request"]
