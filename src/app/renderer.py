from rest_framework.renderers import BaseRenderer
from rest_framework.utils import json

from helpers.responses import AppResponse


class ApiRenderer(BaseRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, AppResponse):
            return data.content

        return AppResponse(data).content
