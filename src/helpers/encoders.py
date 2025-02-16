from functools import wraps
from json import dumps

from django.core.serializers.json import DjangoJSONEncoder


class CustomEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, (list, set, tuple)):
            return [self.default(i) for i in o]
        try:
            return super().default(o)
        except:
            return str(o)


@wraps(dumps)
def custom_json_dumps(*args, **kwargs):
    return dumps(*args, **kwargs, cls=CustomEncoder)
