import json

from sqlalchemy import Column, Integer, DateTime, Enum, JSON

from applications import enum
from exts import db


class Task(db.Model):
    """
    用户将要执行的指令任务
    """
    __tablename__ = 'user_task'

    id = Column(Integer, primary_key=True, autoincrement=True)

    cmd = Column(Enum(enum.Task.cmd), comment='要执行的指令')
    cmd_args = Column(JSON, default={}, nullable=False, comment='指令值所需参数')

    cmd_state = Column(Enum(enum.Task.cmd_state), default=enum.Task.cmd_state.未运行, nullable=False, comment='指令执行状态')
    cmd_info = Column(JSON, default={}, nullable=False, comment='指令执行的信息, 赋值时使用 set_cmd_info 方法')

    exe_count = Column(Integer, default=0, nullable=False, comment='执行的次数, 正常执行的话值是1, 出错重试会累加')

    start_time = Column(DateTime, comment='执行开始时间')
    end_time = Column(DateTime, comment='执行完成时间')

    user_id = Column(Integer, nullable=False, comment='任务所属用户的id')  # ForeignKey column=f'{User.__tablename__}.id'
    device_id = Column(Integer, nullable=False, comment='要执行任务的设备id')  # ForeignKey column=f'{Device.__tablename__}.id'

    def set_cmd_info(self, info: str):
        self.cmd_info = {
            **self.cmd_info,
            self.exe_count: info
        }
