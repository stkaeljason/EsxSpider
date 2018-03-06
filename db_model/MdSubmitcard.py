# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MdSubmitcard(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_submitcard'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement = True)
    service_orderno = Column(String,unique = True)
    service_orderid = Column(String,nullable = True)
    detail_text = Column(String)
    archives = Column(String,nullable=True)
    img = Column(String,nullable=True)
    localtion = Column(String,nullable=True)
    engineer_code1 = Column(String,nullable=True)
    recording = Column(String,nullable=True)
    status = Column(Integer,nullable=True)
    created_at = Column(Integer,nullable=True)
    platform_id = Column(Integer,nullable=True)