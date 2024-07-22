import hashlib


# 密码MD5时用到的 salt, 该变量不可更改, 否则当前全部用户密码均会失效
__salt = '闲鱼助手系统密码salt值: ******'


def password_md5(password: str) -> str:
    return hashlib.md5((password + __salt).encode()).hexdigest()


if __name__ == '__main__':
    print(password_md5('666'))
