from sqlalchemy import Column, Integer, String

from exts import db


class Setting(db.Model):
    """
    系统设置
    """
    __tablename__ = 'sys_setting'

    id = Column(Integer, primary_key=True, autoincrement=True)

    sys_name = Column(String, comment='系统名称')
    sys_logo = Column(String, comment='系统logo')
