from sqlalchemy import Column, Integer, String, Float, Text

from exts import db


class Sub(db.Model):
    """
    系统会员订阅
    """

    __tablename__ = 'sys_sub'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, unique=True, comment='会员订阅的名称')
    price = Column(Float, comment='会员订阅的价格')
    duration = Column(Integer, comment='会员订阅的期间，以天为单位')
    detail = Column(Text, comment='存储订阅计划的优惠详情')
