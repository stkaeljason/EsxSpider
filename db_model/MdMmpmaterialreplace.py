# coding: utf8

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MdMmpmaterialreplace(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_mmpmaterialreplace'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    replace_id = Column(String(100), unique = True)
    replace_code = Column(String(100))
    befor_material_code = Column(String(100),nullable = True)
    befor_material_name = Column(String(100),nullable = True)
    befor_source_material_code = Column(String(100),nullable = True)
    after_material_code = Column(String(600),nullable = True)
    after_material_name = Column(String(110))
    replace_type = Column(String(1000),nullable = True)
    pub_validly = Column(String(110))
    material_code = Column(String(110),nullable = True)
    maint_code = Column(String(120),nullable = True)
    org_code = Column(String(100),nullable = True)
    content_text = Column(String(900),nullable = True)