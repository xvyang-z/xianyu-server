import datetime
from typing import Union

import jwt

from setting import JWT_SECRET_KEY, JWT_EXPIRE_HOURS
from applications.common.user_info import User_Info


token_prefix = 'Bearer '


# 生成token
def create_jwt_token(user_id: int, user_name: str) -> str:
    # 设置token过期时间
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_HOURS)

    # 准备payload，可以根据需要添加更多字段
    payload = {
        'exp': expiration_time,
        'data': {
            'id': user_id,
            'name': user_name
        }
    }
    # 生成JWT token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token_prefix + token


# 校验token
def jwt_token_check(token: str) -> tuple[bool, Union[str, User_Info]]:
    token = token.replace(token_prefix, '')

    try:
        playload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return True, User_Info(
            id_=playload['data']['id'],
            name=playload['data']['name']
        )

    except jwt.exceptions.ExpiredSignatureError:
        return False, "token认证过期"

    except jwt.exceptions.DecodeError:
        return False, "token认证无效"

    except Exception:
        return False, '未知错误'


# 获取过期时间
def jwt_expire_time(token: str) -> tuple[bool, str]:
    token = token.replace(token_prefix, '')

    try:
        playload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return True, datetime.datetime.fromtimestamp(playload['exp']).strftime('%Y-%m-%d %H:%M:%S')

    except jwt.exceptions.ExpiredSignatureError:
        return False, "token认证过期"

    except jwt.exceptions.DecodeError:
        return False, "token认证无效"

    except Exception:
        return False, '未知错误'


if __name__ == '__main__':
    print(
        jwt_expire_time('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjI1Mjk1MTAsImRhdGEiOnsiaWQiOjIsIm5hbWUiOiJhZG1pbiJ9fQ.zgYpmRR5I8LDoOEM0mLAN3az3dwUZzBboCLKPNiB3mE')
    )