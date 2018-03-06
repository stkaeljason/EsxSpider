# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OrderImg(Base):
    # 表的名字:
    __tablename__ = 'dm_order_img'

    # 表的结构:
    oi_id = Column(Integer, primary_key=True)
    oi_img = Column(String)
    oi_ord_id = Column(Integer,nullable=True)
    oi_create_time = Column(Integer,nullable=True)
    oi_group = Column(Integer,nullable=True)
    is_submit = Column(Integer,nullable=True)
    oi_name = Column(String,nullable=True)
    oi_apl_model = Column(String,nullable=True)