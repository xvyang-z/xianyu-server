import os
from pathlib import Path

from setting import PROJECT_ROOT, FILE_UPLOAD_PATH_NAME


class FilePath:
    def __init__(self, abs_path: Path, relative_path: str, router_path: str):
        """
        :param abs_path: 在磁盘上的真实路径
        :param relative_path: 相对于根目录的相对路径
        :param router_path: 前端发起请求时的路由路径, 与相对路径只差最前方的 .
        """
        self.abs_path = abs_path
        self.relative_path = relative_path
        self.router_path = router_path


class UploadPath:
    @staticmethod
    def get_user_dir(user_id: int) -> FilePath:
        """
        获取用户的文件夹, 不存在就创建
        """
        relative_path = f'./{FILE_UPLOAD_PATH_NAME}/user/{user_id}'

        abs_path = PROJECT_ROOT / relative_path
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        return FilePath(abs_path, relative_path, relative_path[1:])

    @staticmethod
    def get_sys_dir():
        """
        获取系统用到的目录, 不存在就创建
        """
        relative_path = f'./{FILE_UPLOAD_PATH_NAME}/sys'

        abs_path = PROJECT_ROOT / relative_path
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        return FilePath(abs_path, relative_path, relative_path[1:])

    @staticmethod
    def get_user_avatar_dir(user_id: int):
        """
        获取用户的头像文件夹, 不存在就创建
        """
        relative_path = f'./{FILE_UPLOAD_PATH_NAME}/user/{user_id}/avatar'

        abs_path = PROJECT_ROOT / relative_path
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        return FilePath(abs_path, relative_path, relative_path[1:])

    @staticmethod
    def get_user_product_dir(user_id: int, product_uuid: str):
        """
        获取用户的商品文件夹, 不存在就创建
        """
        relative_path = f'./{FILE_UPLOAD_PATH_NAME}/user/{user_id}/product_img/{product_uuid}'

        abs_path = PROJECT_ROOT / relative_path
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        return FilePath(abs_path, relative_path, relative_path[1:])

    @staticmethod
    def get_user_publish_dir(user_id: int, product_uuid: str):
        """
        获取用户的商品文件夹, 不存在就创建
        """
        relative_path = f'./{FILE_UPLOAD_PATH_NAME}/user/{user_id}/publish_img/{product_uuid}'

        abs_path = PROJECT_ROOT / relative_path
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        return FilePath(abs_path, relative_path, relative_path[1:])

