# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MideaMmpstore(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_mmpstore'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement = True)
    sale_unit_code = Column(String,unique = True)
    sale_unit_name = Column(String)
    region_code = Column(String)
    created_at = Column(Integer,nullable=True)
    updated_at = Column(Integer,nullable=True)