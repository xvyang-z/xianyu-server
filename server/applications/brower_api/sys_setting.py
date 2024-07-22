import os

from flask import Blueprint

from applications.common.resp import Resp
from applications.library.file_path import UploadPath
from applications.model.sys_setting import Setting
from setting import API_PREFIX, PROJECT_ROOT
from exts import db
from applications.library.parse_req_data import process_requset_data


bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/sys_setting'
)


# 保存系统设置
@bp.route('/save', methods=['POST'])
def save():
    params = process_requset_data()
    sys_name = params['sys_name']
    sys_logo = params['sys_logo']

    sys_setting: Setting = Setting.query.first()

    # 没有则创建, 有则更新
    if sys_setting is None:

        new_setting = Setting(
            sys_name=sys_name,
            sys_logo=sys_logo,
        )
        db.session.add(new_setting)

    else:

        sys_setting.sys_name = sys_name
        sys_setting.sys_logo = sys_logo

    try:
        db.session.commit()

        # 删除旧的logo文件
        sys_dir = UploadPath.get_sys_dir().abs_path
        for img_path in os.listdir(sys_dir):
            sys_logo_file_name = sys_logo.split('/')[-1]
            if sys_logo_file_name != img_path:
                os.remove(sys_dir / img_path)

        return Resp.success('保存成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('保存失败')


# 获取系统设置信息
@bp.route('/info', methods=['GET'])
def info():
    sys_setting: Setting = Setting.query.first()

    if sys_setting is None:
        resp = {
            "sys_name": "",
            "sys_logo": "",
        }
    else:
        resp = {
            "sys_name": sys_setting.sys_name,
            "sys_logo": sys_setting.sys_logo,
        }

    return Resp.success(resp)
