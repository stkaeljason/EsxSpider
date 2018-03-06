# coding: utf8

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class auxAccount(Base):
    # 表的名字:
    __tablename__ = 'dm_aux_account'

    # 表的结构:
    aux_id = Column(Integer, primary_key=True)
    aux_merc_account = Column(String(20))
    password = Column(String(100))
    aux_id_number = Column(String(10))
    aux_adminid = Column(String(11))
    channelid = Column(String(100))
    aux_name = Column(String(32))
    aux_serial_number = Column(String(32))
    aux_phone = Column(String(32))
    aux_archives_number = Column(String(32))
    token = Column(String(100))
    aux_add_time = Column(String(10))