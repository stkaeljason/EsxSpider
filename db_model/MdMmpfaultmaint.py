# coding: utf8

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MdMmpfaultmaint(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_mmpfaultmaint'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    maint_id = Column(String(100), unique = True)
    maint_settlement_id = Column(String(100))
    maint_code = Column(String(100),nullable = True)
    class_code = Column(String(100),nullable = True)
    prod_code_third = Column(String(100),nullable = True)
    reson_desc = Column(String(100),nullable = True)
    maint_desc = Column(String(110),nullable = True)
    maint_settlement_code = Column(String(1000),nullable = True)
    maint_settlement_desc = Column(String(110),nullable = True)
    reson_code = Column(String(110),nullable = True)
    product_code = Column(String(120),nullable = True)
    org_code = Column(String(100),nullable = True)
    content_text = Column(String(900),nullable = True)