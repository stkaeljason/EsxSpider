# coding: utf8

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MdMmpmaterialinfos(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_mmpmaterialinfos'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    material_type_main_code = Column(String(100), unique = True)
    material_type_main_name = Column(String(100))
    material_type_mid_code = Column(String(100),nullable = True)
    material_type_mid_name = Column(String(100),nullable = True)
    material_code = Column(String(100),nullable = True)
    material_name = Column(String(600),nullable = True)
    material_model = Column(String(110))
    material_desc = Column(String(1000),nullable = True)
    storage_qty = Column(String(110))
    maint_code = Column(String(110),nullable = True)
    unit_code = Column(String(120),nullable = True)
    product_code = Column(String(120),nullable = True)
    org_code = Column(String(100),nullable = True)
    prod_code = Column(String(100),nullable = True)
    content_text = Column(String(900),nullable = True)