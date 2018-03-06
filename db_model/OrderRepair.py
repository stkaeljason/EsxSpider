# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrderRepair(Base):
    # 表的名字:
    __tablename__ = 'dm_order_repair'

    # 表的结构:
    or_id = Column(Integer, primary_key=True)
    or_ord_id = Column(Integer)
    or_merc_cost = Column(DECIMAL(10,2),nullable=True)
    or_mast_cost = Column(DECIMAL(10,2),nullable=True)