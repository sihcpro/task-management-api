from typing import Optional, Union

from django.conf import settings
from django.http import HttpRequest

from .encoders import custom_json_dumps
from .required_libs import Request
from .responses import AppResponse

_is_sentry_active = False
if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=settings.SENTRY_INTEGRATIONS,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
    _is_sentry_active = True
    print("Sentry initiated by darasdk")


class AppException(Exception):
    exception_holder = {}

    STATUS_CODE = 500
    MESSAGE = "Application Error"
    NOTIFY = True

    def __init__(
        self,
        errcode: int = 000000,
        message: Optional[str] = None,
        resp_data: Optional[dict] = None,
        err_data: Optional[dict] = None,
        err_message: Optional[str] = None,
        err_info: Optional[dict] = None,
        request: Optional[Union[Request, HttpRequest]] = None,
        log: Optional[bool] = None,
        verbose: Optional[bool] = None,
        notify: Optional[bool] = None,
        log_to_file: Optional[bool] = True,
        error: Optional[Exception] = None,
        err_html: Optional[str] = None,
    ):
        """The base exception class for the application.

        Args:
            errcode (int, optional): This is the distinct code to track the error.
            message (str, optional): This is the response message to be sent to the client.
            resp_data (dict, optional): This is the response data to be sent to the client.
            err_data (dict, optional): This is the error data to debug the error. Will be sent to the client if settings.DEBUG is True.
            err_message (str, optional): This is the error message to debug the error. It will be copied from the error if provided.
            err_info (dict, optional): This is the error information to debug the error. It is collected from the error and the request if provided.
            request (Union[Request, HttpRequest], optional): The request object to debug the error. Should be object of HttpRequest.
            log (bool, optional): True if the error should be logged.
            verbose (bool, optional): True if log the error trace.
            notify (bool, optional): True if the error should be sent to sentry.
            log_to_file (bool, optional): True if the error should be logged to file.
            error (Exception, optional): The error object to debug the error.
        """
        self.errcode = errcode
        self.message = message or self.MESSAGE
        super().__init__(self.message)
        self.resp_data = resp_data or {}
        self.request = request
        self.err_data = err_data if err_data is not None else {}
        self.err_message = err_message or (
            repr(error) if error is not None else self.message
        )
        self.err_html = err_html if err_html is not None else err_message
        self.should_notify = notify
        self._error = error
        self._err_info: dict = (
            err_info
            if isinstance(err_info, dict)
            else ({"info": err_info} if err_info is not None else {})
        )
        self._notified = False

        if error is not None:
            self.with_traceback(error.__traceback__)

    def log_trace_to_err_info(self):
        if "trace" in self._err_info:
            return

        trace = []
        tb = self.__traceback__
        try:
            while tb is not None:
                trace.append(
                    {
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno,
                    }
                )
                tb = tb.tb_next
        except Exception:
            pass
        self._err_info["trace"] = trace
        if self._error is not None:
            self._err_info["type"] = type(self._error).__name__
            self._err_info["message"] = repr(self._error)

    def notify_error(self):
        self._notified = True
        self.notify_sentry()

    def notify_if_needed(self, re_notify=False):
        if self._notified and not re_notify:
            return
        if self.should_notify is True or (self.should_notify is None and self.NOTIFY):
            self.notify_error()

    def notify_sentry(self):
        if not _is_sentry_active:
            return

        sentry_sdk.set_tag("env", settings.ENV)
        sentry_sdk.set_tag("app", settings.SENTRY_APP_NAME)
        sentry_sdk.set_tag("err_code", self.errcode)
        sentry_sdk.set_tag("message", self.message)
        sentry_sdk.set_tag("err_message", self.err_message)
        sentry_sdk.set_tag("err_class", self.__class__.__name__)
        sentry_sdk.set_extra("request_data", self.request_data_str)
        sentry_sdk.set_extra("data", self.data_str)
        sentry_sdk.set_extra("error_info", custom_json_dumps(self.err_info))
        sentry_sdk.set_extra("error_data", custom_json_dumps(self.err_data))
        sentry_sdk.set_extra("response_data", custom_json_dumps(self.resp_data))
        if "device" in self.request_data:
            sentry_sdk.set_context("device", {"name": self.request_data["device"]})
        sentry_sdk.capture_exception(self)
        print("send data to sentry")

    @property
    def request(self) -> Optional[Union[HttpRequest, Request]]:
        return self._request

    @request.setter
    def request(self, value: Optional[Union[HttpRequest, Request]]):
        self._request = value
        if isinstance(value, Request):
            self._http_request = value._request
            self._rest_request = value
        else:
            self._http_request = value
            self._rest_request = None

    @property
    def request_data(self):
        if hasattr(self, "_request_data"):
            return self._request_data

        data = {}
        try:
            data["request"] = {
                "url": self._http_request.path,
                "method": self._http_request.method,
            }
        except Exception:
            try:
                data["request"] = self._http_request.__dict__
            except Exception:
                data["request"] = str(self._request)
        try:
            data["user"] = {
                "id": self._http_request.user.id,
                "username": self._http_request.user.username,
            }
        except Exception:
            data["user"] = None
        try:
            data["request_data"] = self._http_request.data
        except Exception:
            data["request_data"] = None
        try:
            data["param"] = dict(self._http_request.GET.items())
        except Exception:
            data["param"] = None
        try:
            data["device"] = self._http_request.environ["HTTP_USER_AGENT"]
        except Exception:
            data["device"] = "Unknown"

        self._request_data = data
        return self._request_data

    @property
    def request_data_str(self):
        if hasattr(self, "_request_data_str"):
            return self._request_data_str

        self._request_data_str = custom_json_dumps(self.request_data)
        return self._request_data_str

    @property
    def data_str(self):
        if hasattr(self, "_data_str"):
            return self._data_str

        self._data_str = custom_json_dumps(self.err_data)
        return self._data_str

    @property
    def err_info(self) -> dict:
        if not isinstance(self._err_info, dict):
            try:
                self._err_info = dict(self._err_info)
            except Exception:
                self._err_info = {"info": self._err_info}

        self.log_trace_to_err_info()
        return self._err_info

    @property
    def body(self) -> dict:
        result = {
            "success": False,
            "message": self.message,
            "data": self.resp_data,
        }
        result["info"] = {
            "error_code": self.errcode,
            "error_message": self.err_message,
            "error_html": self.err_html,
        }
        if settings.DEBUG:
            result["info"].update(
                {
                    "request_data": self.request_data,
                    "error_info": self.err_info,
                    "error_data": self.err_data,
                }
            )
        return result

    @property
    def resp(self) -> AppResponse:
        return AppResponse(data=self.body, status=self.STATUS_CODE)

    def __del__(self):
        self.notify_if_needed()


class BadRequestException(AppException):
    STATUS_CODE = 400
    MESSAGE = "Bad request"
    NOTIFY = False


class UnauthorizedException(AppException):
    STATUS_CODE = 401
    MESSAGE = "Unauthorized"
    NOTIFY = False


class ForbiddenException(AppException):
    STATUS_CODE = 403
    MESSAGE = "Forbidden"
    NOTIFY = False


class NotFoundException(AppException):
    STATUS_CODE = 404
    MESSAGE = "Item not found"
    NOTIFY = False


class ConflictException(AppException):
    STATUS_CODE = 409
    MESSAGE = "Item exists"
    NOTIFY = False


class ServerErrorException(AppException):
    STATUS_CODE = 500
    MESSAGE = "Server error"
    NOTIFY = True
