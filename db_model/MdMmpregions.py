# coding: utf8

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MdMmpregions(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_mmpregions'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    region_code = Column(String(100), unique = True)
    parent_reg_id = Column(String(100),nullable = True)
    region_level = Column(String(100),nullable = True)
    asst_code = Column(String(110),nullable = True)
    region_desc = Column(String(100),nullable = True)
    zip_code = Column(String(32),nullable = True)
    area_num = Column(String(32),nullable = True)
    longitude = Column(String(32),nullable = True)
    latitude = Column(String(32),nullable = True)
    created_at = Column(Integer,nullable = True)