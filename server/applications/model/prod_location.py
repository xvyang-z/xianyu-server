from sqlalchemy import Integer, Column, String

from exts import db


class Location(db.Model):
    """
    发布商品时选择的位置信息, 这个数据和闲鱼的 省 市 区 保持一致
    """

    __tablename__ = 'prod_location'

    id = Column(Integer, primary_key=True)
    level = Column(Integer)
    parent_id = Column(Integer)
    name = Column(String)
