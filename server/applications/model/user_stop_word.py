from sqlalchemy import Column, Integer, String

from exts import db


class StopWord(db.Model):
    """
    违禁词
    """
    __tablename__ = 'user_stop_word'

    id = Column(Integer, primary_key=True, autoincrement=True)

    word = Column(String, comment='违禁词')

    user_id = Column(Integer, nullable=False, comment='系统用户id')  # ForeignKey(column=f'{User.__tablename__}.id'
