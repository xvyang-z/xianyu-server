from flask import Blueprint, g

from applications.common.resp import Resp
from applications.model.sys_user import User
from setting import API_PREFIX
from exts import db
from applications.library.parse_req_data import process_requset_data
from applications.library.password_md5 import password_md5

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/user_user',
)


# 退出
@bp.route('/logout', methods=['POST'])
def logout():
    return Resp.success(None, '退出成功！')


# 修改密码
@bp.route('/update_password', methods=['POST'])
def update_password():

    params = process_requset_data()

    id_ = g.user_info.id
    old_password = params['old_password']
    new_password = params['new_password']

    user = User.query.get(id_)
    if not user:
        return Resp.fail('没有此用户，密码修改失败！')

    if not user.password == password_md5(old_password):
        return Resp.fail('旧密码不正确，密码修改失败！')

    user.password = password_md5(new_password)

    try:
        db.session.commit()
        return Resp.success(None, '密码修改成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('系统异常，修改失败！')


# 通过登录的用户获取用户信息
@bp.route('/user_info', methods=['GET'])
def user_info():
    user_id: int = g.user_info.id
    user: User = User.query.get(user_id)

    info = {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "desc": user.desc,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "is_vip": user.is_vip,
        'vip_start_date': user.vip_start_date,
        'vip_end_date': user.vip_end_date,
        'vip_auto_renew': user.vip_auto_renew,
        "create_time": user.create_time,
        "update_time": user.update_time,
    }
    return Resp.success(info)
