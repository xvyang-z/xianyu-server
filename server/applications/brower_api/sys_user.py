import os
import shutil
from datetime import datetime

from flask import Blueprint

from applications.common.resp import Resp
from applications.library.file_path import UploadPath
from applications.library.parse_req_data import process_requset_data
from applications.library.password_md5 import password_md5
from applications.model.sys_user import User
from exts import db
from setting import API_PREFIX, DEFAULT_AVATAR_PATH

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/sys_user',
)


# 分页
@bp.route('/paging', methods=['POST'])
def usr_paging():
    params = process_requset_data()

    page: int = params.get('page', 1)
    per_page: int = params.get('per_page', 10)
    username: str = params['query_args'].get("username")
    is_active: bool = params['query_args'].get("is_active")
    is_admin: bool = params['query_args'].get("is_admin")

    query = User.query

    if username:
        query = query.filter(User.username.contains(username))

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)

    paginate = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for item in paginate.items:
        item: User
        items.append({
            "id": item.id,
            "username": item.username,

            "avatar": item.avatar,
            "desc": item.desc,

            "is_active": item.is_active,
            "is_admin": item.is_admin,

            "is_vip": item.is_vip,
            "vip_auto_renew": item.vip_auto_renew,
            "vip_end_date": item.vip_end_date,
            "vip_start_date": item.vip_start_date,

            "create_time": item.create_time,
            "update_time": item.update_time,
        })

    resp = {
        'page': paginate.page,
        'per_page': paginate.per_page,
        'total': paginate.total,
        'items': items,
    }

    return Resp.success(resp)


# 新增
@bp.route('/create', methods=['POST'])
def create():
    params = process_requset_data()
    username: str = params["username"]
    password: str = params["password"]
    is_active: bool = params["is_active"]
    is_admin: bool = params["is_admin"]
    desc: str = params["desc"]

    if User.query.filter_by(username=username).first():
        return Resp.fail('用户名重复！')

    new_user = User(
        username=username,
        password=password_md5(password),
        avatar=DEFAULT_AVATAR_PATH,
        is_active=is_active,
        is_admin=is_admin,
        desc=desc
    )

    db.session.add(new_user)

    try:
        db.session.commit()

        # 创建用户的资源文件夹
        UploadPath.get_user_dir(new_user.id)

        return Resp.success(None, '新增成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('新增失败')


# 删除用户
@bp.route('/delete', methods=['POST'])
def delete():
    params = process_requset_data()
    ids: list[int] = params['ids']

    users: list[User] = User.query.filter(User.id.in_(ids)).all()

    try:
        for user in users:
            db.session.delete(user)

        db.session.commit()

        for user in users:
            user_dir = UploadPath.get_user_dir(user.id).abs_path  # 删除后并提交更改不会影响这个对象实例, 还能取到 id 属性
            shutil.rmtree(user_dir)

        return Resp.success(None, '删除成功！')

    except Exception:
        db.session.rollback()
        return Resp.fail('删除失败')


# 编辑
@bp.route('/update', methods=['POST'])
def update():
    params = process_requset_data()
    id_ = params["id"]

    new_username = params["username"]
    new_avatar = params["avatar"]
    new_desc = params["desc"]

    user: User = User.query.get(id_)

    if user is None:
        return Resp.fail('用户不存在')

    if user.username != new_username and User.query.filter(User.username == new_username).first() is not None:
        return Resp.fail('已存在相同的用户名')

    old_avatar = user.avatar

    user.username = new_username

    # 默认头像就不说了, 确保新头像路径合法, 避免下一次修改头像时意外删除文件
    user_avatar_dir = UploadPath.get_user_avatar_dir(user.id)
    if new_avatar != DEFAULT_AVATAR_PATH and not new_avatar.startswith(user_avatar_dir.router_path):
        return Resp.fail('头像路径非法')

    user.avatar = new_avatar

    user.desc = new_desc
    user.update_time = datetime.utcnow()

    try:
        db.session.commit()

        # 删除旧的用户头像文件
        if old_avatar != DEFAULT_AVATAR_PATH and old_avatar != new_avatar:
            # 在修改一次头像的过程中可能会上传多个, 但仅最后一个会被保留, 这里对头像文件夹进行遍历, 删除所有非新头像的文件
            for avatar_file_name in os.listdir(user_avatar_dir.abs_path):
                if not new_avatar.endswith(avatar_file_name):
                    os.remove(user_avatar_dir.abs_path / avatar_file_name)

        return Resp.success(None, '编辑成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('编辑失败')


# 用户详情
@bp.route('/detail/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    user = User.query.get(user_id)

    resp = {
        "id": user.id,
        "username": user.username,

        "avatar": user.avatar,
        "desc": user.desc,

        "is_active": user.is_active,
        "is_admin": user.is_admin,

        "is_vip": user.is_vip,
        "vip_auto_renew": user.vip_auto_renew,
        "vip_end_date": user.vip_end_date,
        "vip_start_date": user.vip_start_date,

        "create_time": user.create_time,
        "update_time": user.update_time,
    }

    return Resp.success(resp)
