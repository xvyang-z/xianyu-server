import json

from flask import request

from applications import enum
from applications.client_api import __bp
from applications.common.resp import Resp
from applications.enum.model.Task import group_p2d_cmd
from applications.model.user_product_to_device import ProductToDevice
from applications.model.user_task import Task
from exts import db


@__bp.route('/exec_fail', methods=['POST'])
def exec_fail():
    """
    执行失败调用这个接口, 更新任务状态
    """
    task_id: int = request.json['task_id']
    cmd_info: str = request.json['cmd_info']

    task: Task = Task.query.get(task_id)

    task.set_cmd_info(cmd_info)
    task.cmd_state = enum.Task.cmd_state.执行失败

    if task.cmd in group_p2d_cmd:
        p2d_id = task.cmd_args['id']
        p2d: ProductToDevice = ProductToDevice.query.get(p2d_id)
        p2d.is_in_operation = False

    try:
        db.session.commit()
        return Resp.success()
    except Exception as e:
        db.session.rollback()
        return Resp.fail(str(e))
