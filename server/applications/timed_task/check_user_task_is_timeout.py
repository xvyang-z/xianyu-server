import datetime
import time

from flask import Flask
from sqlalchemy import or_

from applications import enum
from applications.enum.model.Task import group_p2d_cmd
from applications.model.user_product_to_device import ProductToDevice
from applications.model.user_task import Task
from exts import db
from setting import CHECK_TIMED_TASK_INTERVAL, TASK_TIMEOUT_THRESHOLD


def check_user_task_is_timeout(app: Flask):
    """
    找出执行超时的任务并设置为超时状态

    :return:
    """
    with app.app_context():
        while True:
            five_minutes_ago = datetime.datetime.now() - TASK_TIMEOUT_THRESHOLD

            # 这一堆是是执行超时的情况, 当客户端网络问题无法发请求时, 任务会一直处于 运行中 或 重试中 状态
            tasks: list[Task] = (
                Task.query
                .filter(
                    or_(
                        Task.cmd_state == enum.Task.cmd_state.运行中,
                        Task.cmd_state == enum.Task.cmd_state.重试中,
                    ),
                    Task.start_time <= five_minutes_ago,
                ).all()
            )

            for task in tasks:
                task.end_time = datetime.datetime.now()
                task.cmd_state = enum.Task.cmd_state.执行超时

                if task.cmd in group_p2d_cmd:
                    p2d_id = task.cmd_args['id']
                    p2d: ProductToDevice = ProductToDevice.query.get(p2d_id)
                    p2d.is_in_operation = False

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

            time.sleep(CHECK_TIMED_TASK_INTERVAL)
