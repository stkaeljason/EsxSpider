# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OrderCode(Base):
    # 表的名字:
    __tablename__ = 'dm_order_code'

    # 表的结构:
    oc_id = Column(Integer, primary_key=True)
    oc_within_code = Column(String)
    oc_abroad_code = Column(String)
    oc_verify_code = Column(String)
    oc_ord_id = Column(Integer)
    oc_is_verifyok = Column(Integer,nullable=True)
    oc_verify_desc = Column(String,nullable=True)
    oc_verify_time = Column(Integer,nullable=True)
    oc_create_time = Column(Integer,nullable=True)
    oc_is_amt = Column(Integer,nullable=True)
    oc_group = Column(Integer,nullable=True)
    is_submit = Column(Integer,nullable=True)
    oc_apl_model = Column(String,nullable=True)