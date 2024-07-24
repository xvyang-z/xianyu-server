import datetime
import json
import shutil

from flask import g
from sqlalchemy import or_

from applications import enum
from applications.client_api import __bp
from applications.common.resp import Resp
from applications.enum.model.Task import group_p2d_cmd
from applications.library.file_path import UploadPath
from applications.model.user_device import Device
from applications.model.user_product_to_device import ProductToDevice
from applications.model.user_task import Task
from exts import db
from setting import TASK_MAX_RETEY


@__bp.route('/get_task', methods=['POST'])
def get_task():
    user_id = g.user_info.id

    to_do_task: list = (
        Task.query
        .join(Device, Task.device_id == Device.id)
        .filter(
            Task.user_id == user_id,
            or_(
                Task.cmd_state == enum.Task.cmd_state.未运行,
                Task.cmd_state == enum.Task.cmd_state.执行失败,
                Task.cmd_state == enum.Task.cmd_state.执行超时,
            ),
            Task.exe_count <= TASK_MAX_RETEY
        )
        .add_columns(Device.device_flag, Device.device_name, Device.is_open_fish_shop)
        .limit(10)
        .all()
    )

    result = []
    for item in to_do_task:
        task: Task = item[0]

        # 跳过重试次数达到上限的
        if task.exe_count == TASK_MAX_RETEY:
            task.cmd_state = enum.Task.cmd_state.次数用尽  # 执行状态不用`执行失败`, 否则下次还会查出来, 这里会被重复执行
            task.end_time = datetime.datetime.utcnow()

            if task.cmd in group_p2d_cmd:
                p2d_id = task.cmd_args['id']
                p2d: ProductToDevice = ProductToDevice.query.get(p2d_id)

                # 商品在点击发布按钮时会被添加到发布管理界面, 状态是待发布, 发布失败自然是要删除
                if task.cmd == enum.Task.cmd.发布商品:
                    db.session.delete(p2d)
                    shutil.rmtree(UploadPath.get_user_publish_dir(g.user_info.id, p2d.uuid).abs_path)

                # 如果是其他的商品操作， 则在次数用尽后需要将操作状态置为 False
                else:
                    p2d.is_in_operation = False

            continue

        # 如果是商品操作, 需要把对应商品的操作状态置为 True
        if task.cmd in group_p2d_cmd:
            p2d_id = task.cmd_args['id']
            p2d: ProductToDevice = ProductToDevice.query.get(p2d_id)
            p2d.is_in_operation = True

        if task.cmd_state == enum.Task.cmd_state.未运行:
            task.cmd_state = enum.Task.cmd_state.运行中

        elif task.cmd_state == enum.Task.cmd_state.执行失败:
            task.cmd_state = enum.Task.cmd_state.重试中

        elif task.start_time == enum.Task.cmd_state.执行超时:
            task.cmd_state = enum.Task.cmd_state.重试中

        task.exe_count += 1  # 执行次数 +1
        task.start_time = datetime.datetime.utcnow()  # 重新设置执行开始时间

        result.append({
            'task_id': task.id,
            'device_flag': item.device_flag,
            'device_name': item.device_name,
            'is_open_fish_shop': item.is_open_fish_shop,
            'cmd': task.cmd,
            'cmd_args': task.cmd_args,
        })

    try:
        db.session.commit()
        return Resp.success(result)
    except Exception as e:
        db.session.rollback()
        return Resp.fail(str(e))


if __name__ == '__main__':
    print(get_task())
