from flask import Blueprint
from flask.globals import g
from sqlalchemy import or_

from applications import enum
from applications.common.resp import Resp
from applications.model.user_task import Task
from applications.model.user_device import Device
from setting import API_PREFIX
from exts import db
from applications.library.parse_req_data import process_requset_data

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/user_task',
)


@bp.route('/paging', methods=['POST'])
def paging():

    params = process_requset_data()

    page = params.get('page', 1)
    per_page = params.get('per_page', 10)

    device_id = params['query_args'].get('device_id')

    query = (
        Task.query
        .join(Device, Task.device_id == Device.id)
        .filter(Task.user_id == g.user_info.id)
        .add_column(Device.device_name)
        .order_by(Task.id.desc())
    )

    if device_id:
        query = query.filter(Task.device_id == device_id)

    paginate = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for item in paginate.items:
        task: Task = item[0]
        items.append({
            'id': task.id,
            'device_name': item.device_name,
            'cmd': task.cmd,
            'cmd_args': task.cmd_args,
            'cmd_state': task.cmd_state,
            'cmd_info': task.cmd_info,
            'start_time': task.start_time,
            'end_time': task.end_time,
        })

    resp = {
        'page': paginate.page,
        'per_page': paginate.per_page,
        'total': paginate.total,
        'items': items,
    }
    return Resp.success(resp)


# 删除任务
@bp.route('/delete', methods=['POST'])
def delete():

    ids = process_requset_data().get('ids')

    running_tasks_num: int = Task.query.filter(
        Task.id.in_(ids),
        or_(
            Task.cmd_state == enum.Task.cmd_state.运行中,
            Task.cmd_state == enum.Task.cmd_state.重试中,
        ),
        Task.user_id == g.user_info.id,
    ).count()

    if running_tasks_num > 0:
        return Resp.fail('不能删除运行中或重试中的任务')

    Task.query.filter(
        Task.id.in_(ids),
        Task.user_id == g.user_info.id
    ).delete()

    try:
        db.session.commit()
        return Resp.success(None, '删除成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('删除失败！')
