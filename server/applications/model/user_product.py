from sqlalchemy import Column, Integer, String, Float, JSON

from exts import db


class Product(db.Model):
    """
    商品
    """
    __tablename__ = 'user_product'

    id = Column(Integer, primary_key=True, autoincrement=True)

    uuid = Column(String, comment='客户端提交的商品唯一标识')
    desc = Column(String, comment='描述信息')
    images = Column(JSON, default=[], nullable=False, comment='商品图片URL列表')
    price = Column(Float, comment='商品价格')
    user_id = Column(Integer, nullable=False, comment='用户id')  # ForeignKey(column=f'{User.__tablename__}.id'
