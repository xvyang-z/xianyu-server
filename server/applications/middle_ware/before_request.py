from flask import request, g

from applications.common.resp import Resp
from setting import IP_ADDRESS_WHITE_LIST, IP_ADDRESS_BLACK_LIST, NOT_TOKEN_PROCESS_ROUTE_LIST
from applications.library.jwt_library import jwt_token_check, token_prefix
from applications.common.user_info import User_Info


def before_request():
    """
    请求前的钩子函数, 进行token判断
    """

    # 请求IP控制
    user_ip = request.remote_addr
    if len(IP_ADDRESS_WHITE_LIST) > 0:
        if user_ip not in IP_ADDRESS_WHITE_LIST:
            return Resp.fail('非法请求')
    if len(IP_ADDRESS_BLACK_LIST) > 0:
        if user_ip in IP_ADDRESS_BLACK_LIST:
            return Resp.fail('非法请求')

    # 设置不需要 token 验证的路由
    if request.path in NOT_TOKEN_PROCESS_ROUTE_LIST \
            or request.path.startswith('/uploads'):
        return None

    # 获取请求头中的 Authorization 进行验证
    authorization = request.headers.get('Authorization')
    if not authorization or not authorization.startswith(token_prefix):
        return Resp.fail('身份验证过期')

    isvalid, data = jwt_token_check(authorization)
    if not isvalid:
        data: str
        return Resp.fail(data)

    data: User_Info
    g.user_info = data
