from flask import Blueprint
from flask.globals import g

from applications import enum
from applications.common.resp import Resp
from applications.library.parse_req_data import process_requset_data
from applications.model.user_task import Task
from exts import db
from setting import API_PREFIX

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


@bp.route('/polish', methods=['POST'])
def polish():
    params = process_requset_data()
    device_ids = params.get("device_ids", [])
    # 加入任务
    for device_id in device_ids:
        # 在这里处理每个设备 ID 的逻辑
        task = Task(
            user_id=g.user_info.id,
            device_id=device_id,
            cmd=enum.Task.cmd.一键擦亮,
        )
        db.session.add(task)
    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 请到任务列表中查看')
    except Exception as e:
        db.session.rollback()
        return Resp.fail('加入任务列表失败!')


@bp.route('/get_coin_and_signin', methods=['POST'])
def get_coin_and_signin():
    params = process_requset_data()
    device_ids = params.get("device_ids", [])
    # 加入任务
    for device_id in device_ids:
        # 在这里处理每个设备 ID 的逻辑
        task = Task(
            user_id=g.user_info.id,
            device_id=device_id,
            cmd=enum.Task.cmd.签到闲鱼币,
        )
        db.session.add(task)
    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 请到任务列表中查看')
    except Exception:
        db.session.rollback()
        return Resp.fail('加入任务列表失败!')


# @bp.route('/promotion', methods=['POST'])
# def promotion():
#     params = process_requset_data()
#     device_id: int = params["id"]
#     desc: str = params["desc"]
#     price: float = params["price"]
#     task = Task(
#         user_id=g.user_info.id,
#         device_id=device_id,
#         cmd_args={'desc': desc, 'price': price},
#         # cmd=
#     )
#     db.session.add(task)
#     try:
#         db.session.commit()
#         return Resp.success(None, '已加入任务列表, 请到任务列表中查看')
#     except Exception:
#         db.session.rollback()
#         return Resp.fail('加入任务列表失败!')
