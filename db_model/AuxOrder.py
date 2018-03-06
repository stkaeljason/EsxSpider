# coding: utf8

from sqlalchemy import Column, String , Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuxOrder(Base):
    # 表的名字:
    __tablename__ = 'dm_aux_order'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    aux_orderno = Column(String(60),unique = True)
    aux_userid = Column(Integer,nullable=True)
    aux_lng = Column(String(60),nullable=True)
    aux_lat = Column(String(60),nullable=True)
    json_detail = Column(String,nullable=True)
    platform_orderid = Column(Integer,nullable=True)
    is_accept = Column(Integer,nullable=True,default = 0)
    is_finish = Column(Integer,nullable=True,default = 0)
    created_at = Column(Integer,nullable=True)
    accepted_at = Column(Integer,nullable=True)
    finished_at = Column(Integer,nullable=True)