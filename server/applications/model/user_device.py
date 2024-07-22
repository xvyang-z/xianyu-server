from sqlalchemy import Column, Integer, String, Boolean

from exts import db
from setting import ADB_TCP_PORT_SUFFIX


class Device(db.Model):
    """
    用户设备
    """
    __tablename__ = 'user_device'

    id = Column(Integer, primary_key=True, autoincrement=True)

    device_name = Column(String, nullable=False, comment='用于前端展示')
    device_flag = Column(String, nullable=False, comment='手机设备 内网ip 或 adb连接标识序列号')

    is_open_fish_shop = Column(Boolean, default=False, nullable=False, comment='闲鱼账户是否开通鱼小铺')

    user_id = Column(Integer, nullable=False, comment='设备所属用户ID')  # ForeignKey(column=f'{User.__tablename__}.id'

    def get_device_flag_without_suffix(self):
        """
        获取不带 ADB_TCP_PORT_SUFFIX 后缀的设备标识
        """
        return self.device_flag.replace(ADB_TCP_PORT_SUFFIX, '')
