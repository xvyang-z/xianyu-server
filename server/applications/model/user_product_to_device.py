from sqlalchemy import Column, Integer, DateTime, String, Float, Boolean, Enum, JSON

from applications import enum
from exts import db


class ProductToDevice(db.Model):
    """
    商品 和 设备 的发布关系
    """
    __tablename__ = 'user_product_to_device'

    id = Column(Integer, primary_key=True, autoincrement=True)

    uuid = Column(String, comment='客户端提交的商品唯一标识')

    desc = Column(String, comment='描述信息')
    images = Column(JSON, default=[], nullable=False, comment='商品图片URL列表')
    price = Column(Float, comment='商品价格')
    location = Column(JSON, default=[], nullable=False, comment='发布位置')

    publish_state = Column(Enum(enum.ProductToDevice.publish_state), nullable=False, comment='发布状态')

    is_in_operation = Column(Boolean, default=True, nullable=False, comment='是否正在被操作中')

    publish_time = Column(DateTime, comment='发布时间')

    user_id = Column(Integer, nullable=False, comment='系统用户的id')  # ForeignKey(column=f'{User.__tablename__}.id'
    device_id = Column(Integer, nullable=False, comment='用户的设备的id')  # ForeignKey(column=f'{Device.__tablename__}.id'
