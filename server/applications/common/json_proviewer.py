from datetime import datetime, timedelta

from flask.json.provider import DefaultJSONProvider


class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            obj = obj + timedelta(hours=8)
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)
