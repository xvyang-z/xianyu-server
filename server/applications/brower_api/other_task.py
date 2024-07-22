import json

from flask import Blueprint
from flask.globals import g

from applications import enum
from applications.common.resp import Resp
from applications.model.user_device import Device
from applications.model.user_product_to_device import ProductToDevice
from applications.model.user_task import Task
from setting import API_PREFIX
from exts import db
from applications.library.parse_req_data import process_requset_data

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/other_task',
)


@bp.route('/open_fish_currency_deduction', methods=['POST'])
def open_fish_currency_deduction():
    params = process_requset_data()
    device_ids = params.get("device_ids", [])
    # 加入任务
    for device_id in device_ids:
        # 在这里处理每个设备 ID 的逻辑
        task = Task(
            user_id=g.user_info.id,
            device_id=device_id,
            cmd=enum.Task.cmd.开启闲鱼币抵扣,
        )
        db.session.add(task)
    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 请到任务列表中查看')
    except Exception:
        db.session.rollback()
        return Resp.fail('加入任务列表失败!')
