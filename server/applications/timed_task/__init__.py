import threading

from flask import Flask

from applications.timed_task.check_user_task_is_timeout import check_user_task_is_timeout


def run_timed_task(app: Flask):
    """
    执行定时任务
    :return:
    """
    threading.Thread(target=check_user_task_is_timeout, args=(app,), daemon=True).start()
