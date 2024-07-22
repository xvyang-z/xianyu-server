from datetime import datetime

from flask.json.provider import DefaultJSONProvider


class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)
