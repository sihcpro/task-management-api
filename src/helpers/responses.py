from json import JSONEncoder
from typing import Any, Dict, Optional, Type

from django.http import JsonResponse

from .encoders import CustomEncoder


class CustomJsonResponse(JsonResponse):
    def __init__(
        self,
        data: Any,
        encoder: Type[JSONEncoder] = CustomEncoder,
        safe: bool = False,
        json_dumps_params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        if (
            data is None
            or isinstance(data, list)
            or (isinstance(data, dict) and "message" not in data)
        ):
            data = {"success": True, "message": "Success", "data": data}
        elif isinstance(data, dict):
            data = {**{"success": True, "message": "Success"}, **data}
        elif isinstance(data, str):
            data = {"success": True, "message": data}

        super().__init__(data, encoder, safe, json_dumps_params, **kwargs)


class AppResponse(CustomJsonResponse):
    """Use this class to return a response from a view."""
