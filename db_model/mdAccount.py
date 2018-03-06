# coding: utf8

from sqlalchemy import Column, String, Integer,Text
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy import create_engine
# engine = create_engine('mysql+mysqlconnector://'+'root'+':'+'root'+'@'+'127.0.0.1'+':'+'3306'+'/'+'ershixiong_anzhuang'+'')

Base = declarative_base()


class MdAccount(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_account'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement=True,unique=True)
    # serviceOrderNo = Column(String(30),nullable=True)
    # serviceUserDemandIds = Column(String(30),nullable=True)\
    work_year = Column(String(10),nullable=True)
    sex = Column(String(5),nullable=True)
    address = Column(String(100),nullable=True)
    unit_name = Column(String(100),nullable=True)
    engineer_id = Column(String(50),nullable=True)
    engineer_code = Column(String(30),nullable=True)
    engineer_level = Column(String(10),nullable=True)
    engineer_tel = Column(String(20),unique=True,nullable=True)
    engineer_name = Column(String(30), nullable=True)   # 师傅姓名
    account_source = Column(String(30), nullable=True)
    engineer_pw = Column(String(20))
    work_no = Column(String(30),nullable=True)
    unit_code = Column(String(20),nullable=True)
    login_ret = Column(Text,nullable=True)
    last_login = Column(Integer,nullable=True)
    # reassignmentReason = Column(String(100),nullable=True)
    # operator = Column(String(20),nullable=True)
    # operateTime = Column(String(30),nullable=True)
    # page = Column(String,nullable=True)
    # pageIndex = Column(String,nullable=True)
    # pageSize = Column(String,nullable=True)
    # rows = Column(String,nullable=True)
    # count = Column(Integer, nullable=True)
    # mapInfo = Column(String,nullable=True)
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)
