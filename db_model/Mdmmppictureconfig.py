# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mdmmppictureconfig(Base):
    # 表的名字:
    __tablename__ = 'dm_midea_mmppictureconfig'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement = True)
    configid = Column(String,unique = True)
    picture_type_name = Column(String)
    picture_number = Column(String)
    created_at = Column(Integer,nullable=True)
    updated_at = Column(Integer,nullable=True)