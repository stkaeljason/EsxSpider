# coding:utf-8
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
# 本地添加表时用
# from sqlalchemy import create_engine
# engine = create_engine('mysql+mysqlconnector://'+'root'+':'+'root'+'@'+'127.0.0.1'+':'+'3306'+'/'+'ershixiong_anzhuang'+'')

Base = declarative_base()


class MdFactory(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_factory_order'

    id = Column(Integer, primary_key=True, autoincrement=True,unique=True)
    factorynumber = Column(String(40),nullable=True,unique=True)
    appoint_time = Column(String(30), nullable=True)
    enginer_name = Column(String(20), nullable=True)
    enginer_code = Column(String(20), nullable=True)
    platform_id = Column(Integer,nullable=True)                 # dm_order表插入订单详情时的id
    accout_source = Column(String(30), nullable=True)
    order_type =  Column(String(16), nullable=True)
    service_order_id = Column(String(40),nullable=True)
    service_user_demandids = Column(String(40),nullable=True)
    factory_data = Column(Text,nullable=True)
    md_orderno = Column(String(40),nullable=True)
    track_text = Column(String(200),nullable=True)
    order_type = Column(String(16),nullable=True)
    installcard_addresstype = Column(String(80),nullable=True)
    installcard_buyaddress_id = Column(String(200),nullable=True)
    installcard_buyaddress_desc = Column(String(200),nullable=True)
    created_at = Column(Integer,nullable=True)
    accepted_at = Column(Integer,nullable=True)
    finished_at = Column(Integer,nullable=True)
    verifyed_at = Column(Integer,nullable=True)
    status = Column(Integer,nullable=True)
    verifyed_admin = Column(Integer,nullable=True)
    process = Column(String(50),nullable=True)

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)