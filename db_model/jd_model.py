# coding: utf8

from sqlalchemy import Column, String, Integer,Text
from sqlalchemy.ext.declarative import declarative_base
from db import engine
# from sqlalchemy import create_engine
# engine = create_engine('mysql+mysqlconnector://'+'root'+':'+'root'+'@'+'127.0.0.1'+':'+'3306'+'/'+'ershixiong_anzhuang'+'')

Base = declarative_base()


class JdAccount(Base):
    # 表的名字:
    __tablename__ = 'dm_jd_account'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement=True,unique=True)
    engineer_name = Column(String(30), nullable=True)   # 师傅姓名
    engineer_tel = Column(String(20),unique=True,nullable=True)
    work_year = Column(String(10),nullable=True)
    sex = Column(String(5),nullable=True)
    address = Column(String(100),nullable=True)
    unit_name = Column(String(100),nullable=True)
    engineer_id = Column(String(50),nullable=True)
    engineer_code = Column(String(30),nullable=True)
    engineer_level = Column(String(10),nullable=True)
    engineer_pw = Column(String(20))
    work_no = Column(String(30),nullable=True)
    unit_code = Column(String(20),nullable=True)
    login_ret = Column(Text,nullable=True)
    last_login = Column(Integer,nullable=True)


class JdMerchant(Base):
    # 表的名字:
    __tablename__ = 'dm_jd_merchant'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement=True,unique=True)
    merchant_id = Column(Integer,nullable=True)
    platform_id = Column(Integer,nullable=True)
    merchant_name = Column(String(100),nullable=True)
    account = Column(String(50),nullable=True)
    password = Column(String(50),nullable=True)
    eid = Column(String(150),nullable=True)
    fp = Column(String(150), nullable=True)
    website_id = Column(String(20), nullable=True)
    is_active = Column(Integer, nullable=True)
    cookie = Column(String(150),nullable=True)
    last_login_time = Column(Integer,nullable=True)
    created_at = Column(Integer,nullable=True)
    updated_at = Column(Integer,nullable=True)


class JdFactory(Base):
    # 表的名字:
    __tablename__ = 'dm_jd_factory_order'

    id = Column(Integer, primary_key=True, autoincrement=True,unique=True)
    factorynumber = Column(String(40),nullable=True,unique=True)
    esx_order_id = Column(Integer,nullable=True)            # dm_order表插入订单详情时的id
    appoint_time = Column(String(20), nullable=True)
    enginer_name = Column(String(20), nullable=True)
    service_order_id = Column(String(40),nullable=True)
    service_user_demandids = Column(String(40),nullable=True)
    created_at = Column(Integer,nullable=True)
    factory_data = Column(Text,nullable=True)
    # orderno = Column(String(40),nullable=True)
    track_text = Column(String(200),nullable=True)
    order_type = Column(String(16),nullable=True)
    installcard_addresstype = Column(String(80),nullable=True)
    installcard_buyaddress_id = Column(String(200),nullable=True)
    installcard_buyaddress_desc = Column(String(200),nullable=True)
    accepted_at = Column(Integer,nullable=True)
    finished_at = Column(Integer,nullable=True)
    verifyed_at = Column(Integer,nullable=True)
    status = Column(Integer,nullable=True)
    verifyed_admin = Column(Integer,nullable=True)
    process = Column(String(50),nullable=True)


def create_table():
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)