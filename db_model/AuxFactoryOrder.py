# coding: utf8

from sqlalchemy import Column, String , Integer ,DECIMAL,alias
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class AuxMerchant(Base):
    # 表的名字:
    __tablename__ = 'dm_auxmerchant'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer)
    account = Column(String(100))
    org_code = Column(String(100))
    account_name = Column(String(100))
    password = Column(String)
    css_account = Column(String(110))
    css_password = Column(String(100))
    css_name = Column(String(110))
    cookie = Column(String(110))
    css_companyid = Column(String(40))
    created_at = Column(Integer,nullable = True)
    updated_at = Column(Integer,nullable = True)

class AuxFactoryOrder(Base):
    # 表的名字:
    __tablename__ = 'dm_auxfactory_order'

    # 表的结构:
    ao_id = Column(Integer, primary_key=True)
    factorynumber = Column(String(40))
    aux_orderno = Column(String(40),nullable=True)
    aux_merc = Column(String(40))
    track_text = Column(String(200),nullable=True)
    order_type = Column(String(16),nullable=True)
    platform_id = Column(Integer,nullable=True)
    standard_amt = Column(DECIMAL(10,2),nullable=True)
    created_at = Column(Integer,nullable=True)
    accepted_at = Column(Integer,nullable=True)
    finished_at = Column(Integer,nullable=True)
    verifyed_at = Column(Integer,nullable=True)
    status = Column(Integer,nullable=True)
    verifyed_admin = Column(Integer,nullable=True)
    auxnode = relationship('AuxMerchant',
                foreign_keys=[aux_merc],
                primaryjoin='AuxMerchant.account == AuxFactoryOrder.aux_merc')