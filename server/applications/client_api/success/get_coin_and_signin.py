import datetime

from applications import enum
from applications.client_api import __bp
from applications.common.resp import Resp
from applications.library.parse_req_data import process_requset_data
from applications.model.user_task import Task
from exts import db


@__bp.route('/success/get_coin_and_signin', methods=['POST'])
def get_coin_and_signin():
    """
    签到闲鱼币成功后调用这个接口
    """

    params = process_requset_data()

    task_id = params['task_id']

    # 标记任务完成
    task: Task = Task.query.get(task_id)
    task.cmd_state = enum.Task.cmd_state.执行成功
    task.set_cmd_info('执行成功')
    task.end_time = datetime.datetime.utcnow()

    try:
        db.session.commit()
        return Resp.success()
    except Exception as e:
        db.session.rollback()
        return Resp.fail(str(e))
