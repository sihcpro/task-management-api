from django.conf import settings
from rest_framework.views import exception_handler

from helpers.exceptions import AppException, ServerErrorException


def json_exception_handler(exc, context):
    """
    Custom exception handler for JSON responses.
    """
    if isinstance(exc, AppException):
        return exc.resp

    app_exc = ServerErrorException(500005, error=exc, request=context["request"])
    return app_exc.resp


def debug_json_exception_handler(exc, context):
    """
    Custom exception handler for JSON responses.
    """
    if isinstance(exc, AppException):
        return exc.resp

    if settings.DEBUG:
        return exception_handler(exc, context)

    app_exc = ServerErrorException(500005, error=exc, request=context["request"])
    return app_exc.resp
