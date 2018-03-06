# coding: utf8

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy import create_engine
# engine = create_engine('mysql+mysqlconnector://'+'root'+':'+'root'+'@'+'127.0.0.1'+':'+'3306'+'/'+'ershixiong_anzhuang'+'')

Base = declarative_base()


class MdMerchant(Base):
    # 表的名字:
    __tablename__ = 'dm_media_merchant'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement=True,unique=True)
    media_merchantid = Column(Integer,nullable=True)
    platform_id = Column(Integer,nullable=True)
    merchant_name = Column(String(100),nullable=True)
    account = Column(String(50),nullable=True)
    password = Column(String(50),nullable=True)
    is_active = Column(Integer)
    cookie = Column(String(150),nullable=True)
    last_login_time = Column(Integer,nullable=True)
    created_at = Column(Integer,nullable=True)
    updated_at = Column(Integer,nullable=True)
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

