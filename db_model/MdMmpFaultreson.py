# coding: utf8

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MdMmpFaultreson(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_mmpfaultreson'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    reson_id = Column(String(100), unique = True)
    fault_code = Column(String(100))
    reson_code = Column(String(100),nullable = True)
    reson_desc = Column(String(100),nullable = True)
    prod_code_third = Column(String(110),nullable = True)
    product_code = Column(String(20),nullable = True)
    org_code = Column(String(100),nullable = True)
    content_text = Column(String(900),nullable = True)