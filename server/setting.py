import os
from pathlib import Path


F_PORT = 80
F_HOST = '0.0.0.0'
F_DEBUG_STATUS = True


# jwt 私钥
JWT_SECRET_KEY = '8UmlG5dcAyPYOFsqTPTX9FgLga4iYkL2pIJQKoG7Z4auoNQVn9hOjYKznFeYJXiS'


# jwt 过期时间 (小时)
JWT_EXPIRE_HOURS = 24 * 30


# 请求接口前缀
API_PREFIX = '/api/v1'
CLIENT_API_PREFIX = '/client_api'

# 无需token认证白名单列表
NOT_TOKEN_PROCESS_ROUTE_LIST = [
    API_PREFIX + '/sys_auth/login',
    API_PREFIX + '/sys_auth/register',
    API_PREFIX + '/sys_auth/captcha',

    CLIENT_API_PREFIX + '/check_token_expire',
]

# IP白名单 长度大于0 表示启用
IP_ADDRESS_WHITE_LIST = []
# IP黑名单 长度大于0 表示启用
IP_ADDRESS_BLACK_LIST = []

# adb无线连接默认的端口, 和客户端的初始化手机脚本中的保持一致
__ADB_TCP_PORT = 5555
ADB_TCP_PORT_SUFFIX = f':{__ADB_TCP_PORT}'

# 任务最大执行次数,
TASK_MAX_RETEY = 3


class DB_CFG:
    host = '127.0.0.1'
    port = 5432
    user = 'postgres'
    passwd = 'e671f758a3c8a8b0ce1c833584398ef0ac661695c968499784d6744dcea640d1'
    db = 'postgres'


class RDB_CFG:
    host = '127.0.0.1'
    port = 6379
    db = 0


# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 资源文件
RESOURCE_DIR = PROJECT_ROOT / '.resource'


# 文件上传位置
FILE_UPLOAD_PATH_NAME = 'uploads'
FILE_UPLOAD_PATH = PROJECT_ROOT / FILE_UPLOAD_PATH_NAME


# 用户的默认头像
DEFAULT_AVATAR_PATH = f'/{FILE_UPLOAD_PATH_NAME}/default_avatar.jpg'


# 创建目录
__path_list = [FILE_UPLOAD_PATH]
for path in __path_list:
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == '__main__':
    ...
