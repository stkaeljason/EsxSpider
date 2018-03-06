# coding: utf8

from sqlalchemy import Column, String , Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrderTracking(Base):
    # 表的名字:
    __tablename__ = 'dm_order_tracking'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement = True)
    operator_id = Column(Integer)
    ord_id = Column(Integer)
    operator_name = Column(String)
    operate_before = Column(String,nullable=True)
    operate_after = Column(String,nullable=True)
    add_time = Column(Integer,nullable=True)
    title = Column(String(200),nullable=True)
    desc = Column(String(200),nullable=True)
    # ord_type = Column(Integer,nullable=True)
