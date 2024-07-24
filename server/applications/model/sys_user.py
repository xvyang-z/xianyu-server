import datetime

from sqlalchemy import Integer, Column, String, Boolean, DateTime

from exts import db
from setting import DEFAULT_AVATAR_PATH


class User(db.Model):
    """
    用户
    """

    __tablename__ = 'sys_user'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 用户基本信息
    username = Column(String, unique=True, nullable=False, comment='用户名')
    password = Column(String, nullable=False, comment='密码')
    avatar = Column(String, default=DEFAULT_AVATAR_PATH, nullable=False, comment='头像路径')
    desc = Column(String, comment='描述')

    # 用户系统信息
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    is_admin = Column(Boolean, default=True, nullable=False, comment='是否为管理员')  # fixme 测试 记得改成 False

    # 用户vip信息
    is_vip = Column(Boolean, default=False, nullable=False, comment='是否是会员')
    vip_start_date = Column(DateTime, comment='会员订阅开始时间')
    vip_end_date = Column(DateTime, comment='会员订阅到期时间')
    vip_auto_renew = Column(Boolean, default=False, nullable=False, comment='是否自动续订vip')

    create_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, comment='创建时间')
    update_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, comment='更新时间')
