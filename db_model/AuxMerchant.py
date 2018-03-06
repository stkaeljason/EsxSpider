# coding: utf8

from db_model.db import DBSession
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuxMerchant(Base):
    # 表的名字:
    __tablename__ = 'dm_auxmerchant'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer)
    account = Column(String(100))
    password = Column(String)
    org_code = Column(String(100))
    account_name = Column(String(100))
    is_active = Column(Integer,nullable=True)
    css_account = Column(String(110))
    css_password = Column(String(100))
    css_name = Column(String(110))
    default_master = Column(String(100))
    cookie = Column(String(110))
    css_companyid = Column(String(40))
    created_at = Column(Integer,nullable = True)
    updated_at = Column(Integer,nullable = True)


def query_aux_merchant():
    session = DBSession()
    rs = session.query(AuxMerchant).filter(AuxMerchant.is_active == 0)
    return rs