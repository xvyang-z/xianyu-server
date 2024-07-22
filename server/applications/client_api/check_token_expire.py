from flask import request

from applications.client_api import __bp
from applications.common.resp import Resp
from applications.library.jwt_library import jwt_expire_time


@__bp.route('/check_token_expire', methods=['POST'])
def check_token_expire():
    token: str = request.json['token']

    ok, expire_time = jwt_expire_time(token)
    if not ok:
        return Resp.fail(expire_time)

    return Resp.success(expire_time)