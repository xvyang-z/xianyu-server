import datetime
import json

from applications import enum
from applications.client_api import __bp
from applications.common.resp import Resp
from applications.library.parse_req_data import process_requset_data
from applications.model.user_product_to_device import ProductToDevice
from applications.model.user_task import Task
from exts import db


@__bp.route('/success/republish', methods=['POST'])
def republish():
    """
    重新上架成功后调用这个接口
    """
    params = process_requset_data()

    task_id = params['task_id']

    # 标记任务完成
    task: Task = Task.query.get(task_id)
    task.cmd_state = enum.Task.cmd_state.执行成功
    task.set_cmd_info('执行成功')
    task.end_time = datetime.datetime.utcnow()

    # 更新对应的 发布表 ProductToDevice 中的数据为已发布状态
    id_ = task.cmd_args['id']

    p2d: ProductToDevice = ProductToDevice.query.get(id_)
    p2d.publish_state = enum.ProductToDevice.publish_state.已发布
    p2d.is_in_operation = False
    p2d.publish_time = datetime.datetime.utcnow()

    try:
        db.session.commit()
        return Resp.success()
    except Exception as e:
        db.session.rollback()
        return Resp.fail(str(e))
